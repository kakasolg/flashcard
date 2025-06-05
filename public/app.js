import { auth, realtimeDb } from './firebase.js';
import {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/11.8.0/firebase-auth.js";
import { ref, set, get, child, onValue } from "https://www.gstatic.com/firebasejs/11.8.0/firebase-database.js";

const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const signupButton = document.getElementById('signup-button');
const loginButton = document.getElementById('login-button');
const logoutButton = document.getElementById('logout-button');
const authContainer = document.getElementById('auth-container');
const flashcardContainer = document.getElementById('flashcard-container');
const flashcardForm = document.getElementById('flashcard-form');
const questionInput = document.getElementById('question');
const answerInput = document.getElementById('answer');
const flashcardsList = document.getElementById('flashcards-list');

// Review Section Elements
const reviewSection = document.getElementById('review-section');
const reviewQuestion = document.getElementById('review-question');
const reviewAnswer = document.getElementById('review-answer');
const showAnswerButton = document.getElementById('show-answer-button');
const reviewControls = document.getElementById('review-controls');
const customIntervalSelect = document.getElementById('custom-interval');
const submitReviewButton = document.getElementById('submit-review-button');
const easeButtons = document.querySelectorAll('.ease-button');

let currentReviewingCardId = null; // To keep track of the card being reviewed
let currentReviewingCardData = null;
let selectedEase = null;

// --- Mock SRS Engine Intervals (mirroring core/srs_engine.py) ---
const CUSTOM_SRS_INTERVALS = {
    "1_hour": "1 Hour",
    "3_hours": "3 Hours",
    "24_hours": "24 Hours",
    "3_days": "3 Days",
    "7_days": "7 Days",
};

function populateCustomIntervals() {
    for (const key in CUSTOM_SRS_INTERVALS) {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = CUSTOM_SRS_INTERVALS[key];
        customIntervalSelect.appendChild(option);
    }
}
// --- End Mock SRS ---


// Sign up new users
signupButton.addEventListener('click', async () => {
    const email = emailInput.value;
    const password = passwordInput.value;
    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        console.log('Signed up:', userCredential.user);
    } catch (error) {
        console.error('Error signing up:', error);
    }
});

// Log in existing users
loginButton.addEventListener('click', async () => {
    const email = emailInput.value;
    const password = passwordInput.value;
    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        console.log('Logged in:', userCredential.user);
    } catch (error) {
        console.error('Error logging in:', error);
    }
});

// Log out users
logoutButton.addEventListener('click', async () => {
    try {
        await signOut(auth);
        console.log('Logged out');
    } catch (error) {
        console.error('Error logging out:', error);
    }
});

// Listen for authentication state changes
onAuthStateChanged(auth, (user) => {
    if (user) {
        // User is signed in
        authContainer.style.display = 'none';
        flashcardContainer.style.display = 'block';
        logoutButton.style.display = 'block';
        if (user) {
            loadFlashcards(user.uid);
            populateCustomIntervals(); // Populate dropdown on login
            // TODO: Add logic to actually start a review session, e.g., by clicking a "Review Due Cards" button
            // For now, let's imagine a card is loaded for review:
            // displayCardForReview({ cardId: "mock123", question: "Test Q", answer: "Test A", current_interval_key: "1_hour" });
        }
    } else {
        // User is signed out
        authContainer.style.display = 'block';
        flashcardContainer.style.display = 'none';
        logoutButton.style.display = 'none';
        flashcardsList.innerHTML = ''; // Clear flashcards when logged out
        reviewSection.style.display = 'none'; // Hide review section
        customIntervalSelect.innerHTML = '<option value="">Let Engine Decide</option>'; // Reset dropdown
    }
});

// Add new flashcard
flashcardForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = questionInput.value;
    const answer = answerInput.value;
    const user = auth.currentUser;

    if (user) {
        const flashcardId = Date.now().toString(); // Simple unique ID
        const now = new Date();
        const initialIntervalKey = "1_hour"; // Default for new cards
        let initialNextReviewDate = new Date(now);
        initialNextReviewDate.setHours(now.getHours() + 1); // Default to 1 hour from now

        try {
            await set(ref(realtimeDb, `users/${user.uid}/flashcards/${flashcardId}`), {
                question: question,
                answer: answer,
                creation_date: now.toISOString(),
                last_reviewed_date: null, // Not reviewed yet
                next_review_date: initialNextReviewDate.toISOString(),
                current_interval_key: initialIntervalKey,
                ease_history: []
            });
            questionInput.value = '';
            answerInput.value = '';
            console.log('Flashcard added');
        } catch (error) {
            console.error('Error adding flashcard:', error);
        }
    }
});

// Load and display flashcards
function loadFlashcards(userId) {
    const flashcardsRef = ref(realtimeDb, `users/${userId}/flashcards`);
    onValue(flashcardsRef, (snapshot) => {
        flashcardsList.innerHTML = ''; // Clear existing list
        const data = snapshot.val();
        if (data) {
            Object.keys(data).forEach((key) => {
                const flashcard = data[key];
                const listItem = document.createElement('li');
                listItem.innerHTML = `
                    <div>
                        <strong>Q:</strong> ${flashcard.question} <br>
                        <strong>A:</strong> ${flashcard.answer} <br>
                        <small>Next Review: ${flashcard.next_review_date ? new Date(flashcard.next_review_date).toLocaleString() : 'N/A'}</small><br>
                        <small>Interval: ${CUSTOM_SRS_INTERVALS[flashcard.current_interval_key] || flashcard.current_interval_key || 'N/A'}</small>
                    </div>
                    <button class="review-button" data-card-id="${key}">Review This Card</button>
                `;
                // Add event listener to the review button
                listItem.querySelector('.review-button').addEventListener('click', () => {
                    displayCardForReview({ cardId: key, ...flashcard });
                });
                flashcardsList.appendChild(listItem);
            });
        } else {
            flashcardsList.innerHTML = '<li>No flashcards yet.</li>';
        }
    });
}

function displayCardForReview(card) {
    currentReviewingCardId = card.cardId;
    currentReviewingCardData = card; // Store full card data
    reviewQuestion.textContent = card.question;
    reviewAnswer.textContent = card.answer;
    reviewAnswer.parentElement.style.display = 'none'; // Hide answer initially
    showAnswerButton.style.display = 'inline-block';
    reviewControls.style.display = 'none';
    reviewSection.style.display = 'block';
    selectedEase = null; // Reset selected ease
    customIntervalSelect.value = ""; // Reset custom interval
    easeButtons.forEach(btn => btn.classList.remove('selected'));
}

showAnswerButton.addEventListener('click', () => {
    reviewAnswer.parentElement.style.display = 'block';
    showAnswerButton.style.display = 'none';
    reviewControls.style.display = 'block';
});

easeButtons.forEach(button => {
    button.addEventListener('click', () => {
        selectedEase = button.dataset.ease;
        easeButtons.forEach(btn => btn.classList.remove('selected'));
        button.classList.add('selected');
        console.log(`Ease selected: ${selectedEase}`);
    });
});

submitReviewButton.addEventListener('click', async () => {
    if (!selectedEase) {
        alert("Please select how well you recalled the card.");
        return;
    }
    if (!currentReviewingCardId || !auth.currentUser) {
        console.error("No card being reviewed or user not logged in.");
        return;
    }

    const user = auth.currentUser;
    const chosenIntervalKey = customIntervalSelect.value;

    // --- This is where the call to the actual SRS engine would happen on a backend ---
    // For now, we'll simulate the logic and directly calculate the next review date.
    // This simplified client-side logic should ideally be replaced by a call to a serverless function
    // that runs the Python `SpacedRepetitionEngine`.

    let nextIntervalKey = currentReviewingCardData.current_interval_key || "1_hour";
    const intervals = Object.keys(CUSTOM_SRS_INTERVALS);
    let currentIndex = intervals.indexOf(nextIntervalKey);

    if (chosenIntervalKey) {
        nextIntervalKey = chosenIntervalKey;
    } else {
        if (selectedEase === "easy") {
            currentIndex = Math.min(intervals.length - 1, currentIndex + 1);
        } else if (selectedEase === "hard") {
            currentIndex = 0; // Reset to the shortest interval
        }
        // For "medium", interval remains the same (currentIndex doesn't change unless it was the first review)
        nextIntervalKey = intervals[currentIndex];
    }

    const now = new Date();
    let nextReviewDate = new Date(now);

    // Simplified timedelta calculation (mirroring Python's timedelta logic)
    const intervalParts = nextIntervalKey.split('_');
    const value = parseInt(intervalParts[0]);
    const unit = intervalParts[1];

    if (unit === "hour" || unit === "hours") {
        nextReviewDate.setHours(now.getHours() + value);
    } else if (unit === "days" || unit === "day") {
        nextReviewDate.setDate(now.getDate() + value);
    }
    // --- End of simplified client-side SRS logic ---

    try {
        const cardRef = ref(realtimeDb, `users/${user.uid}/flashcards/${currentReviewingCardId}`);
        // Update only specific fields, preserving others like question and answer
        const updates = {
            last_reviewed_date: now.toISOString(),
            next_review_date: nextReviewDate.toISOString(),
            current_interval_key: nextIntervalKey,
            // ease_history: firebase.database.ServerValue.increment(1) // More complex update needed for array
        };
         // To update ease_history, you might fetch the card, update array, then set, or use a transaction.
        // For simplicity, not updating ease_history array here.

        await set(ref(realtimeDb, `users/${user.uid}/flashcards/${currentReviewingCardId}`), {
            ...currentReviewingCardData, // keep existing data
            last_reviewed_date: now.toISOString(),
            next_review_date: nextReviewDate.toISOString(),
            current_interval_key: nextIntervalKey,
        });

        console.log(`Review submitted for card ${currentReviewingCardId}. Ease: ${selectedEase}, Chosen Interval: ${chosenIntervalKey || 'Engine Decided'}`);
        console.log(`Next review date: ${nextReviewDate.toLocaleString()}, New interval key: ${nextIntervalKey}`);

        reviewSection.style.display = 'none'; // Hide review section after submission
        loadFlashcards(user.uid); // Reload flashcards to show updated review times
        // TODO: Load next due card for review
    } catch (error) {
        console.error("Error submitting review:", error);
    }
});
