const SUBTEMPLATE_DESCRIPTIONS = {
    // Basic Frameworks
    "5 E's Lesson Plan": "Engage, Explore, Explain, Elaborate, and Evaluate framework for inquiry-based learning",
    "Lesson Seed": "Basic lesson structure with essential components and flexible adaptation options",
    "Horizontal Lesson Planner": "Timeline-based lesson organization with clear progression of activities",
    "SPARK Lesson": "Structured, Progressive, Active, Reflective, Knowledge-based approach to lesson design",
    
    // Learning Approaches
    "Student-Centered Approach": "Focuses on active learning and student engagement through collaborative activities",
    "Project Based Learning": "Long-term learning through complex, authentic projects and real-world challenges",
    "Team Based Activity": "Collaborative learning experiences that promote cooperation and communication",
    "Universal Design for Learning": "Inclusive teaching approach accommodating diverse learning styles and needs",
    
    // Content Organization
    "Unit Plan": "Comprehensive overview of connected lessons and learning objectives",
    "Book Summary": "Structured outline for literature analysis and key concepts",
    "Vocabulary List": "Organized collection of key terms with definitions and usage examples",
    "Notes Outline": "Hierarchical organization of lesson content and key points",
    
    // Special Focus
    "STEM Project": "Integrated science, technology, engineering, and math activities",
    "Technology Integration": "Strategic incorporation of digital tools and resources",
    "Lab + Material List": "Detailed preparation guide for hands-on experimental activities",
    "Learning Situations": "Context-rich scenarios for authentic learning experiences",
    
    // Question Types
    "Multiple Choice Questions": "Traditional format testing with options for varied difficulty levels",
    "Word Problems": "Application-based questions requiring problem-solving skills",
    "Fill In The Blank": "Completion-style questions focusing on key concepts",
    "True/False Questions": "Quick assessment of factual understanding",
    
    // Evaluation Tools
    "Analytic Rubric": "Detailed scoring guide with specific criteria and performance levels",
    "Holistic Rubric": "Overall assessment tool with comprehensive performance descriptions",
    "Assessment Outline": "Framework for evaluating student learning and progress",
    "Evidence Statements": "Clear indicators of student understanding and achievement",
    
    // Interactive Activities
    "Think-Pair-Share": "Structured discussion method promoting individual and collaborative learning",
    "Jigsaw Activity": "Cooperative learning strategy where students become experts on content",
    "Round Robin": "Group activity format ensuring equal participation from all students",
    "4 Corners": "Movement-based activity for expressing opinions and discussing topics",
    
    // Learning Games
    "Bingo Style": "Engaging review game format using recognition and recall",
    "Jeopardy Style": "Competitive question-and-answer game for content review",
    "Quiz Quiz Trade": "Active learning strategy combining movement and peer review",
    "Escape Room": "Problem-solving adventure with curriculum-based challenges",
    
    // Engagement Tools
    "Class Poll": "Quick feedback tool for gathering student opinions and understanding",
    "Self-Assessment": "Reflective tool for students to evaluate their own learning",
    "Reflective Journaling": "Written reflection on learning experiences and progress",
    "Mad Lib": "Creative writing activity with parts of speech practice",
    
    // Social Learning
    "Team Building Activity": "Exercises designed to improve group dynamics and cooperation",
    "S.E.L. Activity": "Social-emotional learning experiences for personal growth",
    "Mindfulness Activity": "Exercises promoting focus and emotional awareness",
    "Conversation Practice": "Structured dialogue activities for language and communication skills"
};

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
    const personalizationModal = new bootstrap.Modal(document.getElementById('personalizationModal'));

    // Get templates data from global variable
    const templatesData = window.TEMPLATES_DATA || {};
    templateModal.show();

    // Template variables
    let selectedTemplate = '';
    let currentSubtemplate = '';

    // DOM elements
    const templateCards = document.querySelectorAll('.template-card');
    const selectedTemplateDisplay = document.getElementById('selectedTemplate');
    const selectedSubtemplateDisplay = document.getElementById('selectedSubtemplate');
    const subtemplateButton = document.getElementById('subtemplateButton');
    const subtemplateContent = document.getElementById('subtemplateContent');
    const lessonForm = document.getElementById('lessonForm');
    const lessonOutput = document.getElementById('lessonPlanOutput');
    const changeTemplateBtn = document.getElementById('changeTemplate');
    const toggleAdvancedBtn = document.getElementById('toggleAdvanced');
    const advancedFields = document.getElementById('advancedFields');
    const sidebar = document.getElementById('historySidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const closeSidebar = document.getElementById('closeSidebar');
    const personalizationForm = document.getElementById('personalizationForm');


    // Sidebar Toggle
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.add('active');
    });

    closeSidebar.addEventListener('click', () => {
        sidebar.classList.remove('active');
    });

    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
        if (sidebar.classList.contains('active') &&
            !sidebar.contains(e.target) &&
            !sidebarToggle.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });

    // Template selection
    templateCards.forEach(card => {
        card.addEventListener('click', () => {
            selectedTemplate = card.dataset.template;
            templateCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selectedTemplateDisplay.textContent = card.querySelector('h4').textContent;
            updateSubtemplates(selectedTemplate);

            // Force close the modal
            const modalInstance = bootstrap.Modal.getInstance(templateModalEl);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    });

    // Change template button
    changeTemplateBtn.addEventListener('click', () => {
        templateModal.show();
    });

    // Show subtemplate modal
    subtemplateButton.addEventListener('click', () => {
        subtemplateModal.show();
    });

    // Update subtemplates based on selected template
    function updateSubtemplates(template) {
        const subtemplates = templatesData[template]?.subtemplates || {};

        subtemplateContent.innerHTML = Object.entries(subtemplates).map(([category, items]) => `
            <div class="subtemplate-category mb-4">
                <h5 class="mb-3">${category}</h5>
                <div class="row g-3">
                    ${items.map(item => `
                        <div class="col-md-6">
                            <div class="subtemplate-item" data-subtemplate="${item}">
                                <div class="d-flex justify-content-between align-items-start">
                                    <span>${item}</span>
                                    <i class="fas fa-info-circle text-primary" 
                                       data-bs-toggle="tooltip" 
                                       data-bs-placement="top" 
                                       title="${SUBTEMPLATE_DESCRIPTIONS[item] || 'Description coming soon'}"></i>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');

        // Initialize tooltips for new content
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(el => new bootstrap.Tooltip(el));

        // Add click handlers for subtemplate items
        const subtemplateItems = document.querySelectorAll('.subtemplate-item');
        subtemplateItems.forEach(item => {
            item.addEventListener('click', () => {
                // Remove selected class from all items
                subtemplateItems.forEach(i => i.classList.remove('selected'));
                // Add selected class to clicked item
                item.classList.add('selected');
                // Update the subtemplate button text
                const selectedSubtemplateText = item.querySelector('span').textContent;
                document.getElementById('selectedSubtemplate').textContent = selectedSubtemplateText;
                // Store the selected subtemplate
                currentSubtemplate = selectedSubtemplateText;
                // Close the modal
                subtemplateModal.hide();
            });
        });
    }

    // Load history from localStorage
    // Toggle arrow rotation
    document.querySelector('.card-title').addEventListener('click', function() {
        const arrow = this.querySelector('.fa-chevron-down');
        const output = document.getElementById('lessonPlanOutput');
        
        if (output.style.display === 'none') {
            output.style.display = 'block';
            arrow.style.transform = 'rotate(0deg)';
        } else {
            output.style.display = 'none';
            arrow.style.transform = 'rotate(-90deg)';
        }
    });

    const loadHistory = () => {
        const history = JSON.parse(localStorage.getItem('lessonHistory') || '[]');
        const historyContainer = document.getElementById('lessonHistory');
        historyContainer.innerHTML = history.map((item, index) => `
            <div class="list-group-item list-group-item-action" role="button" onclick="loadLessonPlan(${index})">
                <div class="d-flex justify-content-between align-items-center">
                    <h5 class="mb-1">${item.title}</h5>
                    <small>${new Date(item.timestamp).toLocaleDateString()}</small>
                </div>
                <p class="mb-1">${item.subject} - ${item.grade || 'No grade specified'}</p>
            </div>
        `).join('') || '<p class="text-muted p-3">No plans yet</p>';
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

    // Load a lesson plan from history
    window.loadLessonPlan = (index) => {
        const history = JSON.parse(localStorage.getItem('lessonHistory') || '[]');
        if (history[index]) {
            const plan = history[index];
            displayLessonPlan(plan);
            sidebar.classList.remove('active');
        }
    };


    

    // Form submission
    lessonForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        if (!selectedTemplate) {
            alert('Please select a template first');
            templateModal.show();
            return;
        }

        const submitBtn = this.querySelector('button[type="submit"]');
        const spinner = submitBtn.querySelector('.spinner-border');
        const originalBtnText = submitBtn.textContent;

        // Show loading state
        submitBtn.disabled = true;
        spinner.classList.remove('d-none');
        submitBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status"></span>
            Generating...
        `;

        // Show loading in output area
        lessonOutput.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary mb-3" role="status"></div>
                <p class="text-muted">Generating your plan...</p>
            </div>
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
            submitBtn.textContent = originalBtnText;
        }
    });

    // Initial history load
    loadHistory();

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

        // Add resources section
        const resourcesTemplate = document.getElementById('resourcesTemplate').innerHTML;
        lessonOutput.insertAdjacentHTML('beforeend', resourcesTemplate);

        // Generate resources based on the lesson plan
        generateResources(data);
    }

    // Add personalization handling
    personalizationForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const preferences = {
            grade: formData.get('defaultGrade'),
            duration: formData.get('defaultDuration'),
            teachingPreferences: formData.get('teachingPreferences')
        };
        localStorage.setItem('teacherPreferences', JSON.stringify(preferences));

        // Update form fields with saved preferences
        document.querySelector('[name="grade"]').value = preferences.grade;
        document.querySelector('[name="duration"]').value = preferences.duration;

        // Close modal using Bootstrap's modal instance
        const personalizationModal = bootstrap.Modal.getInstance(document.getElementById('personalizationModal'));
        personalizationModal.hide();
    });

    // Load saved preferences on page load
    const loadSavedPreferences = () => {
        const preferences = JSON.parse(localStorage.getItem('teacherPreferences') || '{}');
        if (preferences.grade) {
            document.querySelector('[name="grade"]').value = preferences.grade;
        }
        if (preferences.duration) {
            document.querySelector('[name="duration"]').value = preferences.duration;
        }
    };


    // Call loadSavedPreferences on page load
    loadSavedPreferences();


    // Export functionality
    document.getElementById('exportPDF').addEventListener('click', function() {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        const content = lessonOutput.innerText;
        const splitContent = doc.splitTextToSize(content, 180);
        doc.text(splitContent, 15, 15);
        doc.save('lesson_plan.pdf');
    });

    document.getElementById('exportWord').addEventListener('click', function() {
        const content = lessonOutput.innerHTML;
        const blob = new Blob([`
            <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; }
                    </style>
                </head>
                <body>${content}</body>
            </html>
        `], { type: 'application/msword' });

        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'lesson_plan.doc';
        link.click();
    });

    // Add resource generation function
    async function generateResources(data) {
        const prompt = `Based on this lesson plan about "${data.title}", suggest:
        1. Three relevant educational YouTube videos (titles only)
        2. Three worksheet or material ideas
        Keep suggestions concise and directly related to the lesson content.`;

        try {
            const response = await fetch('/generate_resources', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });

            if (!response.ok) throw new Error('Failed to generate resources');

            const resources = await response.json();

            // Update resources in the UI
            const videoContainer = document.querySelector('.video-resources');
            const worksheetContainer = document.querySelector('.worksheet-resources');

            videoContainer.innerHTML = resources.videos.map(video => `
                <div class="resource-item">
                    <i class="fas fa-play-circle text-danger me-2"></i>
                    ${video}
                </div>
            `).join('');

            worksheetContainer.innerHTML = resources.worksheets.map(worksheet => `
                <div class="resource-item">
                    <i class="fas fa-file-download text-primary me-2"></i>
                    ${worksheet}
                </div>
            `).join('');
        } catch (error) {
            console.error('Error generating resources:', error);
        }
    }
});