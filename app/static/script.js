document.addEventListener('DOMContentLoaded', () => {
    // --- Tags Input Handler ---
    const tagContainers = [
        { id: 'tech-skills', defaultTags: ['Python', 'SQL', 'React', 'Docker'] },
        { id: 'languages', defaultTags: ['Python', 'JavaScript', 'HTML/CSS'] },
        { id: 'soft-skills', defaultTags: ['Problem-solving', 'Communication'] },
        { id: 'interests', defaultTags: ['Machine Learning', 'Web Applications'] },
        { id: 'career-interests', defaultTags: ['AI & Big Data', 'Web Design'] }
    ];

    const tagData = {};

    tagContainers.forEach(container => {
        const wrapper = document.getElementById(`${container.id}-container`);
        const input = document.getElementById(`${container.id}-input`);
        
        tagData[container.id] = [...container.defaultTags];
        
        // Render default tags
        renderTags(container.id);

        // Keydown listener on inputs
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                let val = input.value.trim().replace(/,/g, '');
                if (val && !tagData[container.id].includes(val)) {
                    tagData[container.id].push(val);
                    renderTags(container.id);
                }
                input.value = '';
            }
        });
    });

    function renderTags(id) {
        const wrapper = document.getElementById(`${id}-container`);
        const input = document.getElementById(`${id}-input`);
        
        // Remove existing tags
        const tags = wrapper.querySelectorAll('.tag');
        tags.forEach(t => t.remove());

        // Recreate tags before the input element
        tagData[id].forEach((tagText, idx) => {
            const tagEl = document.createElement('span');
            tagEl.className = 'tag';
            tagEl.innerHTML = `${tagText} <i class="fa-solid fa-xmark" data-index="${idx}"></i>`;
            
            // Remove handler
            tagEl.querySelector('i').addEventListener('click', (e) => {
                const indexToRemove = parseInt(e.target.getAttribute('data-index'));
                tagData[id].splice(indexToRemove, 1);
                renderTags(id);
            });

            wrapper.insertBefore(tagEl, input);
        });
    }

    // --- Slider Value Tracker ---
    const expSlider = document.getElementById('years_of_experience');
    const expVal = document.getElementById('exp-val');
    expSlider.addEventListener('input', (e) => {
        expVal.textContent = e.target.value;
    });

    // --- API Health Check ---
    const healthBadge = document.getElementById('health-badge');
    
    async function checkHealth() {
        try {
            const res = await fetch('/api/v1/health');
            if (res.ok) {
                const data = await res.json();
                if (data.status === 'healthy') {
                    healthBadge.className = 'badge badge-online';
                    healthBadge.innerHTML = '<i class="fa-solid fa-circle-check"></i> API Online';
                    return;
                }
            }
            throw new Error();
        } catch (e) {
            healthBadge.className = 'badge badge-offline';
            healthBadge.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> API Offline';
        }
    }

    checkHealth();

    // --- Form Submission & Predictions ---
    const form = document.getElementById('recommendation-form');
    const welcomeState = document.getElementById('welcome-state');
    const loadingState = document.getElementById('loading-state');
    const resultsState = document.getElementById('results-state');

    // Result card nodes
    const topCareerTitle = document.getElementById('top-career-title');
    const topCareerDesc = document.getElementById('top-career-desc');
    const topReasonText = document.getElementById('top-reason-text');
    const topMatchScoreText = document.getElementById('top-match-score');
    const topProgressRing = document.getElementById('top-progress-ring');
    const recommendationsList = document.getElementById('recommendations-list-container');

    // Star feedback properties
    let selectedRating = 0;
    let topMatchTitle = '';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // 1. Enter Loading State
        welcomeState.classList.add('hidden');
        resultsState.classList.add('hidden');
        loadingState.classList.remove('hidden');

        // Reset feedback state
        selectedRating = 0;
        resetStars();
        document.getElementById('feedback-text').value = '';
        document.getElementById('feedback-message').classList.add('hidden');

        // 2. Prepare Payload
        const payload = {
            education_level: document.getElementById('education_level').value,
            degree_branch: document.getElementById('degree_branch').value.trim(),
            technical_skills: tagData['tech-skills'],
            programming_languages: tagData['languages'],
            soft_skills: tagData['soft-skills'],
            interests: tagData['interests'],
            years_of_experience: parseFloat(expSlider.value),
            preferred_domain: document.getElementById('preferred_domain').value,
            preferred_job_type: document.getElementById('preferred_job_type').value,
            career_interests: tagData['career-interests']
        };

        try {
            // 3. Hit API
            const response = await fetch('/api/v1/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error("Analysis failed");
            }

            const data = await response.json();
            const recommendations = data.recommendations;

            // 4. Render recommendations
            if (recommendations && recommendations.length > 0) {
                // Populate Top Match
                const topMatch = recommendations[0];
                topMatchTitle = topMatch.career;
                topCareerTitle.textContent = topMatch.career;
                topMatchScoreText.textContent = `${Math.round(topMatch.match_score)}%`;
                topReasonText.textContent = topMatch.reason;

                // Query database dynamically for description (or fallback)
                fetchCareerDescription(topMatch.career, topCareerDesc);

                // Set circle stroke-dashoffset
                setCircleProgress(topMatch.match_score, topProgressRing);

                // Populate Accordion for remaining recommendations
                recommendationsList.innerHTML = '';
                recommendations.forEach((rec, idx) => {
                    // Create accordion items
                    const recCard = document.createElement('div');
                    recCard.className = `career-item ${idx === 0 ? 'active' : ''}`; // first expanded by default
                    
                    const skillsExistingHtml = rec.existing_skills.map(s => `<span class="skill-badge skill-badge-existing">${s}</span>`).join('') 
                        || '<span class="skill-badge-none">No matching skills</span>';
                    const skillsMissingHtml = rec.missing_skills.map(s => `<span class="skill-badge skill-badge-missing">${s}</span>`).join('')
                        || '<span class="skill-badge-none">No missing skills! Fully compatible.</span>';
                    const roadmapHtml = rec.suggested_learning_areas.map(item => `<li class="roadmap-item"><i class="fa-solid fa-circle-arrow-right"></i> ${item}</li>`).join('');

                    recCard.innerHTML = `
                        <div class="career-item-header">
                            <div class="career-header-info">
                                <h3>${rec.career}</h3>
                                <span>Domain Category Match</span>
                            </div>
                            <div class="career-header-score">
                                <span class="score-badge">${Math.round(rec.match_score)}% Fit</span>
                                <i class="fa-solid fa-chevron-down arrow-icon"></i>
                            </div>
                        </div>
                        <div class="career-item-content">
                            <div class="career-details-body">
                                <p class="career-details-desc italic text-secondary" id="desc-accordion-${idx}">Loading role overview...</p>
                                <p class="hero-reason-box text-sm"><i class="fa-solid fa-lightbulb"></i> <span>${rec.reason}</span></p>
                                <div class="details-row-2">
                                    <div class="skills-column existing">
                                        <h4><i class="fa-solid fa-circle-check"></i> Matching Skills</h4>
                                        <div class="skills-grid">${skillsExistingHtml}</div>
                                    </div>
                                    <div class="skills-column missing">
                                        <h4><i class="fa-solid fa-circle-exclamation"></i> Skills Gap</h4>
                                        <div class="skills-grid">${skillsMissingHtml}</div>
                                    </div>
                                </div>
                                <div class="roadmap-box">
                                    <h4><i class="fa-solid fa-map-location-dot"></i> Suggested Study Roadmap</h4>
                                    <ul class="roadmap-list">${roadmapHtml}</ul>
                                </div>
                            </div>
                        </div>
                    `;

                    // Fetch description dynamically for accordion item
                    const descContainer = recCard.querySelector(`#desc-accordion-${idx}`);
                    fetchCareerDescription(rec.career, descContainer);

                    // Add toggler handler for accordion header
                    recCard.querySelector('.career-item-header').addEventListener('click', () => {
                        const isActive = recCard.classList.contains('active');
                        // Close all
                        const activeItems = recommendationsList.querySelectorAll('.career-item.active');
                        activeItems.forEach(item => item.classList.remove('active'));
                        // Open current if it wasn't active
                        if (!isActive) {
                            recCard.classList.add('active');
                        }
                    });

                    recommendationsList.appendChild(recCard);
                });

                // Show Results Card
                loadingState.classList.add('hidden');
                resultsState.classList.remove('hidden');

                // Smooth Scroll to Results
                resultsState.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                throw new Error("No recommendations returned");
            }
        } catch (err) {
            console.error(err);
            alert("Failed to analyze profile. Make sure the ML model is trained first!");
            loadingState.classList.add('hidden');
            welcomeState.classList.remove('hidden');
        }
    });

    // --- Circular Progress Calculations ---
    function setCircleProgress(percent, circle) {
        const radius = circle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        
        const offset = circumference - (percent / 100) * circumference;
        circle.style.strokeDashoffset = offset;
    }

    // --- Fetch descriptions from Database via API ---
    const careerDescriptionsCache = {};

    async function fetchCareerDescription(title, containerElement) {
        if (careerDescriptionsCache[title]) {
            containerElement.textContent = careerDescriptionsCache[title];
            return;
        }

        try {
            // First fetch the list of careers to get the ID matching the title
            const res = await fetch('/api/v1/careers/');
            if (res.ok) {
                const careers = await res.json();
                const matched = careers.find(c => c.title.toLowerCase() === title.toLowerCase());
                if (matched) {
                    // Fetch full career details
                    const detailRes = await fetch(`/api/v1/careers/${matched.id}`);
                    if (detailRes.ok) {
                        const detail = await detailRes.json();
                        careerDescriptionsCache[title] = detail.description;
                        containerElement.textContent = detail.description;
                        return;
                    }
                }
            }
            throw new Error();
        } catch (e) {
            containerElement.textContent = "A specialized tech role matching your skill profile.";
        }
    }

    // --- Feedback Stars Management ---
    const stars = document.querySelectorAll('.star-rating-container .star, #star-rating-container .star');
    stars.forEach(star => {
        star.addEventListener('click', (e) => {
            selectedRating = parseInt(e.target.getAttribute('data-value'));
            highlightStars(selectedRating);
        });

        star.addEventListener('mouseover', (e) => {
            const hoverVal = parseInt(e.target.getAttribute('data-value'));
            highlightStars(hoverVal);
        });

        star.addEventListener('mouseleave', () => {
            highlightStars(selectedRating);
        });
    });

    function highlightStars(rating) {
        stars.forEach(star => {
            const val = parseInt(star.getAttribute('data-value'));
            if (val <= rating) {
                star.className = 'fa-solid fa-star star active';
            } else {
                star.className = 'fa-regular fa-star star';
            }
        });
    }

    function resetStars() {
        stars.forEach(star => {
            star.className = 'fa-regular fa-star star';
        });
    }

    // --- Submit Feedback ---
    const submitFeedbackBtn = document.getElementById('submit-feedback-btn');
    const feedbackMessage = document.getElementById('feedback-message');
    
    submitFeedbackBtn.addEventListener('click', async () => {
        if (selectedRating === 0) {
            alert("Please select a star rating first.");
            return;
        }

        const comment = document.getElementById('feedback-text').value.trim();
        const payload = {
            career_title: topMatchTitle,
            rating: selectedRating,
            feedback: comment || null
        };

        try {
            const response = await fetch('/api/v1/feedback/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                feedbackMessage.classList.remove('hidden');
                // Disable button and input
                setTimeout(() => {
                    feedbackMessage.classList.add('hidden');
                }, 3000);
            } else {
                alert("Failed to submit feedback. Please try again.");
            }
        } catch (e) {
            console.error(e);
            alert("Network error. Could not save feedback.");
        }
    });
});
