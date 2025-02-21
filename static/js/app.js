document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize modals
    const templateModalEl = document.getElementById('templateModal');
    const templateModal = new bootstrap.Modal(templateModalEl);
    const subtemplateModal = new bootstrap.Modal(document.getElementById('subtemplateModal'));

    // Template variables
    let selectedTemplate = '';
    let currentSubtemplate = '';

    // DOM elements
    const templateCards = document.querySelectorAll('.template-card');
    const selectedTemplateDisplay = document.getElementById('selectedTemplate');
    const subtemplateButton = document.getElementById('subtemplateButton');
    const subtemplateContent = document.getElementById('subtemplateContent');
    const lessonForm = document.getElementById('lessonForm');
    const lessonOutput = document.getElementById('lessonPlanOutput');
    const sidebar = document.getElementById('historySidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const closeSidebar = document.getElementById('closeSidebar');

    // Sidebar Toggle
    sidebarToggle?.addEventListener('click', () => {
        sidebar.classList.add('active');
    });

    closeSidebar?.addEventListener('click', () => {
        sidebar.classList.remove('active');
    });

    // Template selection
    templateCards.forEach(card => {
        card.addEventListener('click', () => {
            selectedTemplate = card.dataset.template;
            templateCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selectedTemplateDisplay.textContent = card.querySelector('h4').textContent;
            updateSubtemplates(selectedTemplate);
            templateModal.hide();
        });
    });

    // Form submission
    lessonForm?.addEventListener('submit', async function(e) {
        e.preventDefault();

        if (!selectedTemplate) {
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
            objectives: this.elements.objectives?.value || ''
        };

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Failed to generate plan');
            }

            const data = await response.json();
            displayLessonPlan(data);
            saveToHistory(data, formData);

        } catch (error) {
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

    // Load history from localStorage
    const loadHistory = () => {
        const history = JSON.parse(localStorage.getItem('lessonHistory') || '[]');
        const historyContainer = document.getElementById('lessonHistory');
        if (historyContainer) {
            historyContainer.innerHTML = history.map((item, index) => `
                <div class="list-group-item list-group-item-action" role="button" onclick="loadLessonPlan(${index})">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-1">${item.title}</h5>
                        <small>${new Date(item.timestamp).toLocaleDateString()}</small>
                    </div>
                    <p class="mb-1">${item.subject} - ${item.grade || 'No grade specified'}</p>
                </div>
            `).join('') || '<p class="text-muted p-3">No plans yet</p>';
        }
    };

    // Save to history
    const saveToHistory = (lessonPlan, formData) => {
        const history = JSON.parse(localStorage.getItem('lessonHistory') || '[]');
        history.unshift({
            ...lessonPlan,
            ...formData,
            timestamp: new Date().toISOString()
        });
        localStorage.setItem('lessonHistory', JSON.stringify(history.slice(0, 10)));
        loadHistory();
    };

    // Display lesson plan
    function displayLessonPlan(data) {
        if (!data.objectives || !Array.isArray(data.objectives)) {
            console.error('Invalid objectives data:', data.objectives);
            data.objectives = ['No objectives specified'];
        }

        const createSection = (title, content, summary) => `
            <div class="content-section">
                <div class="section-header" onclick="this.nextElementSibling.classList.toggle('expanded')">
                    <h4>${title}</h4>
                    <div class="section-summary">
                        ${Array.isArray(summary) ? `<p>${summary[0]}</p>` : ''}
                    </div>
                </div>
                <div class="section-content">
                    ${content}
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
    }

    // Initial history load
    loadHistory();
});
