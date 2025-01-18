document.addEventListener('DOMContentLoaded', function() {
    // Populate locations dropdown
    const locationSelect = document.getElementById('location');
    
    fetch('/locations')
        .then(response => response.json())
        .then(locations => {
            locations.forEach(location => {
                const option = document.createElement('option');
                option.value = location;
                option.textContent = location;
                locationSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Failed to load locations:', error);
            // Add a default option if locations can't be loaded
            const option = document.createElement('option');
            option.value = "Conference Room A";
            option.textContent = "Conference Room A";
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
        
        const eventData = {
            name: document.getElementById('name').value,
            start_time: new Date(document.getElementById('start-time').value).toISOString(),
            end_time: new Date(document.getElementById('end-time').value).toISOString(),
            location: document.getElementById('location').value,
            description: document.getElementById('description').value
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
                result.className = 'success';
                result.textContent = `Event created successfully! Event ID: ${data.event_id}`;
                form.reset();
            } else {
                result.className = 'error';
                result.textContent = data.detail || 'Failed to create event';
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

    // Add validation for end time being after start time
    const startTimeInput = document.getElementById('start-time');
    const endTimeInput = document.getElementById('end-time');

    function updateMinEndTime() {
        endTimeInput.min = startTimeInput.value;
        if (endTimeInput.value && endTimeInput.value < startTimeInput.value) {
            endTimeInput.value = startTimeInput.value;
        }
    }

    startTimeInput.addEventListener('change', updateMinEndTime);
    
    // Set min datetime to now for start time
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    startTimeInput.min = now.toISOString().slice(0, 16);
    updateMinEndTime();
}); 