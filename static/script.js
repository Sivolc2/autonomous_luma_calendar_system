document.addEventListener('DOMContentLoaded', function() {
    // Initialize datetime pickers
    const commonConfig = {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        minuteIncrement: 15,
        time_24hr: false,
        allowInput: true,
        position: "auto",
        theme: "airbnb"
    };

    // Get current date/time and add 1 hour for default start time
    const now = new Date();
    // Round to nearest 15 minutes
    now.setMinutes(Math.ceil(now.getMinutes() / 15) * 15);
    const defaultStart = new Date(now);
    defaultStart.setHours(defaultStart.getHours() + 1);
    // Default end time is 1 hour after start
    const defaultEnd = new Date(defaultStart);
    defaultEnd.setHours(defaultEnd.getHours() + 1);

    // Start time picker
    const startPicker = flatpickr("#start-time", {
        ...commonConfig,
        minDate: "today",
        defaultDate: defaultStart,
        onChange: function(selectedDates) {
            if (selectedDates.length === 0) return;
            
            const startDate = selectedDates[0];
            // Update end time min date when start time changes
            endPicker.set('minDate', startDate);
            
            // If end time is before new start time or not set, update it to start + 1 hour
            if (!endPicker.selectedDates[0] || endPicker.selectedDates[0] < startDate) {
                const newEndDate = new Date(startDate);
                newEndDate.setHours(newEndDate.getHours() + 1);
                endPicker.setDate(newEndDate);
            }
        }
    });

    // End time picker
    const endPicker = flatpickr("#end-time", {
        ...commonConfig,
        minDate: defaultStart,
        defaultDate: defaultEnd,
        onChange: function(selectedDates) {
            if (selectedDates.length === 0) return;
            
            // Update start time max date when end time changes
            startPicker.set('maxDate', selectedDates[0]);
        }
    });

    // Map tooltip functionality
    const mapButton = document.querySelector('.map-button');
    const mapTooltip = document.getElementById('map-tooltip');
    const mapTooltipClose = document.querySelector('.map-tooltip-close');

    mapButton.addEventListener('click', function(e) {
        e.preventDefault();
        mapTooltip.classList.remove('hidden');
        // Add animation class
        requestAnimationFrame(() => {
            mapTooltip.classList.add('map-tooltip-visible');
        });
    });

    function closeMap() {
        mapTooltip.classList.remove('map-tooltip-visible');
        // Wait for animation to finish before hiding
        setTimeout(() => {
            mapTooltip.classList.add('hidden');
        }, 200);
    }

    mapTooltipClose.addEventListener('click', closeMap);

    // Close map when clicking outside
    document.addEventListener('click', function(e) {
        if (!mapTooltip.classList.contains('hidden') && 
            !mapTooltip.contains(e.target) && 
            !mapButton.contains(e.target)) {
            closeMap();
        }
    });

    // Prevent clicks inside map from closing it
    mapTooltip.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Close map on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !mapTooltip.classList.contains('hidden')) {
            closeMap();
        }
    });

    // Populate locations dropdown
    const locationSelect = document.getElementById('location');
    
    fetch('/locations')
        .then(response => response.json())
        .then(rooms => {
            // Add default option
            const defaultOption = document.createElement('option');
            defaultOption.value = "";
            defaultOption.textContent = "Choose a space";
            defaultOption.disabled = true;
            defaultOption.selected = true;
            locationSelect.appendChild(defaultOption);

            // Group rooms by building
            const roomsByBuilding = rooms.reduce((acc, room) => {
                if (!acc[room.building]) {
                    acc[room.building] = [];
                }
                acc[room.building].push(room);
                return acc;
            }, {});

            // Create optgroups for each building
            for (const [building, buildingRooms] of Object.entries(roomsByBuilding)) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = `${building} Laguna St`;
                
                // Sort rooms alphabetically
                buildingRooms.sort((a, b) => a.name.localeCompare(b.name));
                
                buildingRooms.forEach(room => {
                    const option = document.createElement('option');
                    option.value = room.name;
                    option.textContent = room.name;
                    option.title = room.description;  // Add description as tooltip
                    optgroup.appendChild(option);
                });
                
                locationSelect.appendChild(optgroup);
            }
        })
        .catch(error => {
            console.error('Failed to load locations:', error);
            // Add a default option if locations can't be loaded
            const option = document.createElement('option');
            option.value = "Hogwarts Hall";
            option.textContent = "Hogwarts Hall";
            locationSelect.appendChild(option);
        });

    // Check API status
    fetch('/health')
        .then(response => response.json())
        .then(health => {
            if (health.debug_mode) {
                document.getElementById('api-status').textContent = '🔧 Running in debug mode with mock data';
                document.getElementById('api-status').classList.remove('hidden');
            } else if (!health.integrations.luma) {
                document.getElementById('api-status').classList.remove('hidden');
            }
        })
        .catch(() => {
            document.getElementById('api-status').classList.remove('hidden');
        });

    const form = document.getElementById('event-form');
    const result = document.getElementById('result');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Creating...';
        
        // Get the selected dates from flatpickr
        const startDate = startPicker.selectedDates[0];
        const endDate = endPicker.selectedDates[0];
        
        const eventData = {
            name: document.getElementById('name').value,
            start_time: startDate.toISOString(),  // This will be in UTC
            end_time: endDate.toISOString(),      // This will be in UTC
            location: document.getElementById('location').value,
            description: document.getElementById('description').value || undefined,  // Don't send empty string
            host_email: document.getElementById('host-email').value
        };

        try {
            const response = await fetch('/events/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventData)
            });

            const data = await response.json();

            if (response.ok) {
                // Fetch the event details to get the public URL
                const eventDetailsResponse = await fetch(`/events/${data.event_id}`, {
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (eventDetailsResponse.ok) {
                    const eventDetails = await eventDetailsResponse.json();
                    result.className = 'success';
                    result.innerHTML = `
                        Event created successfully!<br>
                        <a href="${eventDetails.url}" target="_blank" class="event-link">
                            View Event on Luma
                            <span class="external-link-icon">↗</span>
                        </a>
                    `;
                } else {
                    // Fallback to showing just the success message if we can't get the URL
                    result.className = 'success';
                    result.textContent = 'Event created successfully!';
                }
                
                form.reset();
                startPicker.clear();
                endPicker.clear();
            } else {
                result.className = 'error';
                if (response.status === 409) {
                    // Format conflict details
                    const conflicts = data.conflicts || [];
                    const conflictDetails = conflicts.map(conflict => 
                        `• ${conflict.name} (${new Date(conflict.start_time).toLocaleTimeString()} - ${new Date(conflict.end_time).toLocaleTimeString()})`
                    ).join('\n');
                    
                    result.innerHTML = `Cannot create event due to conflicts:<br>${conflictDetails || 'Time slot is already booked'}`;
                } else {
                    result.textContent = data.detail || 'Failed to create event';
                }
            }
        } catch (error) {
            result.className = 'error';
            result.textContent = 'Error: Could not connect to the server';
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Create Event';
        }

        result.classList.remove('hidden');
        result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
}); 