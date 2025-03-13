document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize modals
    const templateModalEl = document.getElementById('templateModal');
    if (!templateModalEl) {
        console.error('Template modal element not found');
        return;
    }

    const templateModal = new bootstrap.Modal(templateModalEl, {
        backdrop: 'static',
        keyboard: false
    });

    // Template variables
    let selectedTemplate = '';
    let currentSubtemplate = '';

    // DOM elements
    const templateCards = document.querySelectorAll('.template-card');
    const selectedTemplateDisplay = document.getElementById('selectedTemplate');
    const lessonForm = document.getElementById('lessonForm');
    const lessonOutput = document.getElementById('lessonPlanOutput');
    const sidebar = document.getElementById('historySidebar');
    const closeSidebar = document.getElementById('closeSidebar');

    console.log('Initial setup complete:', {
        templateCardsCount: templateCards.length,
        hasSelectedTemplateDisplay: !!selectedTemplateDisplay,
        hasLessonForm: !!lessonForm,
        pathname: window.location.pathname
    });

    // Show template modal on page load for /app route
    if (window.location.pathname === '/app') {
        console.log('Showing template modal');
        templateModal.show();
    }

    // Template selection
    templateCards.forEach(card => {
        card.addEventListener('click', () => {
            const template = card.dataset.template;
            console.log('Template card clicked:', template);

            if (!template) {
                console.error('No template data attribute found');
                return;
            }

            selectedTemplate = template;
            templateCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');

            if (selectedTemplateDisplay) {
                selectedTemplateDisplay.textContent = card.querySelector('h4').textContent;
                console.log('Updated selected template display:', selectedTemplateDisplay.textContent);
            }

            templateModal.hide();
        });
    });

    // Change template button
    document.getElementById('changeTemplate')?.addEventListener('click', () => {
        console.log('Change template clicked');
        templateModal.show();
    });

    // Sidebar functionality
    if (sidebar && closeSidebar) {
        closeSidebar.addEventListener('click', () => {
            sidebar.classList.remove('active');
        });
    }

    // Display lesson plan with expandable sections
    function displayLessonPlan(data) {
        console.log('Displaying lesson plan:', data);

        if (!data || typeof data !== 'object') {
            console.error('Invalid lesson plan data');
            return;
        }

        if (!data.objectives || !Array.isArray(data.objectives)) {
            console.warn('Invalid objectives data:', data.objectives);
            data.objectives = ['No objectives specified'];
        }

        const createSection = (title, content, summary) => `
            <div class="content-section mb-4">
                <div class="section-header d-flex justify-content-between align-items-center" 
                     onclick="this.closest('.content-section').querySelector('.section-content').classList.toggle('show')">
                    <h4 class="mb-0">${title}</h4>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="section-content collapse">
                    <div class="section-summary text-muted mb-2">
                        ${Array.isArray(summary) ? summary[0] || '' : ''}
                    </div>
                    <div class="section-details">
                        ${content}
                    </div>
                </div>
            </div>
        `;

        const html = `
            <h3 class="mb-4">${data.title || 'Untitled Plan'}</h3>
            ${createSection('Overview',
                `<p>${data.overview || 'No overview provided'}</p>`,
                data.overview_summary)}
            ${createSection('Objectives',
                `<ul>${(data.objectives || []).map(obj => `<li>${obj}</li>`).join('')}</ul>`,
                data.objectives_summary)}
            ${createSection('Materials',
                `<ul>${(data.materials || []).map(mat => `<li>${mat}</li>`).join('')}</ul>`,
                data.materials_summary)}
            ${createSection('Procedure',
                `<ol>${(data.procedure || []).map(step => `<li>${step}</li>`).join('')}</ol>`,
                data.procedure_summary)}
            ${createSection('Assessment',
                `<p>${data.assessment || 'No assessment provided'}</p>`,
                data.assessment_summary)}
            ${createSection('Extensions',
                `<ul>${(data.extensions || []).map(ext => `<li>${ext}</li>`).join('')}</ul>`,
                data.extensions_summary)}
        `;

        lessonOutput.innerHTML = html;

        // Show first section by default
        const firstSection = lessonOutput.querySelector('.section-content');
        if (firstSection) {
            firstSection.classList.add('show');
        }
    }

    // Form submission
    lessonForm?.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Form submitted');

        if (!selectedTemplate) {
            console.error('No template selected');
            alert('Please select a template first');
            templateModal.show();
            return;
        }

        const submitBtn = this.querySelector('button[type="submit"]');
        const spinner = submitBtn.querySelector('.spinner-border');

        // Show loading state
        submitBtn.disabled = true;
        spinner.classList.remove('d-none');
        submitBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status"></span>
            Generating...
        `;

        const formData = {
            template: selectedTemplate,
            subtemplate: currentSubtemplate,
            subject: this.elements.subject.value,
            grade: this.elements.grade?.value || '',
            duration: this.elements.duration?.value || '',
            objectives: this.elements.requirements?.value || ''
        };

        console.log('Sending form data:', formData);

        try {
            // Save preferences first
            const preferencesResponse = await fetch('/api/save_preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!preferencesResponse.ok) {
                console.warn('Failed to save preferences:', await preferencesResponse.text());
            }

            // Generate lesson plan
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Received response:', data);

            displayLessonPlan(data);
            saveToHistory(data, formData);

        } catch (error) {
            console.error('Error:', error);
            lessonOutput.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle"></i>
                    Error: ${error.message}
                </div>
            `;
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            spinner.classList.add('d-none');
            submitBtn.textContent = 'Generate Plan';
        }
    });

    // Load saved preferences when page loads
    async function loadUserPreferences() {
        try {
            const response = await fetch('/api/get_preferences');
            if (response.ok) {
                const preferences = await response.json();
                if (preferences) {
                    // Fill form fields with saved preferences
                    const form = document.getElementById('lessonForm');
                    if (form) {
                        if (preferences.subject) form.elements.subject.value = preferences.subject;
                        if (preferences.grade) form.elements.grade.value = preferences.grade;
                        if (preferences.duration) form.elements.duration.value = preferences.duration;
                        if (preferences.objectives) form.elements.requirements.value = preferences.objectives;
                    }
                }
            }
        } catch (error) {
            console.error('Error loading preferences:', error);
        }
    }

    // Load preferences when page loads
    if (document.getElementById('lessonForm')) {
        loadUserPreferences();
    }

    // Load history from localStorage
    const loadHistory = () => {
        const history = JSON.parse(localStorage.getItem('lessonHistory') || '[]');
        const historyContainer = document.getElementById('lessonHistory');
        if (historyContainer) {
            historyContainer.innerHTML = history.map((item, index) => `
                <div class="list-group-item list-group-item-action" role="button" onclick="loadLessonPlan(${index})">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-1">${item.title || 'Untitled Plan'}</h5>
                        <small>${new Date(item.timestamp).toLocaleDateString()}</small>
                    </div>
                    <p class="mb-1">${item.subject || 'No subject'}</p>
                </div>
            `).join('') || '<p class="text-muted p-3">No plans yet</p>';
        }
    };

    // Save to history
    const saveToHistory = (lessonPlan, formData) => {
        try {
            const history = JSON.parse(localStorage.getItem('lessonHistory') || '[]');
            history.unshift({
                ...lessonPlan,
                ...formData,
                timestamp: new Date().toISOString()
            });
            localStorage.setItem('lessonHistory', JSON.stringify(history.slice(0, 10)));
            loadHistory();
        } catch (error) {
            console.error('Error saving to history:', error);
        }
    };

    // Load lesson plan from history
    window.loadLessonPlan = (index) => {
        try {
            const history = JSON.parse(localStorage.getItem('lessonHistory') || '[]');
            if (index >= 0 && index < history.length) {
                displayLessonPlan(history[index]);
            } else {
                console.error("Invalid lesson plan index");
            }
        } catch (error) {
            console.error('Error loading lesson plan:', error);
        }
    };

    // Initial history load
    loadHistory();
});