<template>
  <transition name="fade">
    <div v-if="showFeedback" class="feedback-collector">
      <div class="feedback-content">
        <h4>How was this response?</h4>
        
        <div class="rating-buttons">
          <button 
            v-for="rating in 5" 
            :key="rating"
            @click="submitRating(rating)"
            :class="{ active: selectedRating === rating }"
            class="rating-btn"
          >
            {{ rating <= selectedRating ? '★' : '☆' }}
          </button>
        </div>

        <div v-if="selectedRating" class="feedback-form">
          <textarea
            v-model="feedbackText"
            placeholder="Any additional feedback? (optional)"
            rows="3"
          ></textarea>
          
          <div class="feedback-actions">
            <button @click="submitFeedback" class="submit-btn">
              Submit Feedback
            </button>
            <button @click="dismissFeedback" class="dismiss-btn">
              Skip
            </button>
          </div>
        </div>

        <button @click="dismissFeedback" class="close-btn">×</button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { api } from '../services/api'
import { selfImprovement } from '../services/selfImprovement'

const props = defineProps({
  responseId: String,
  messageContent: String,
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'submitted'])

const showFeedback = ref(props.show)
const selectedRating = ref(0)
const feedbackText = ref('')

watch(() => props.show, (newVal) => {
  showFeedback.value = newVal
  if (newVal) {
    // Reset form when showing
    selectedRating.value = 0
    feedbackText.value = ''
  }
})

const submitRating = (rating) => {
  selectedRating.value = rating
  
  // Track immediate rating interaction
  selfImprovement.trackInteraction('rating_click', {
    rating,
    responseId: props.responseId
  }, { rating })
}

const submitFeedback = async () => {
  try {
    // Submit to API
    await api.rateResponse(
      props.responseId,
      selectedRating.value,
      feedbackText.value
    )

    // Track successful submission
    selfImprovement.trackInteraction('feedback_submitted', {
      rating: selectedRating.value,
      hasText: !!feedbackText.value,
      responseId: props.responseId
    }, { success: true })

    emit('submitted', {
      rating: selectedRating.value,
      feedback: feedbackText.value
    })

    dismissFeedback()
  } catch (error) {
    console.error('Failed to submit feedback:', error)
    
    // Track failure
    selfImprovement.trackInteraction('feedback_submitted', {
      error: error.message
    }, { success: false })
  }
}

const dismissFeedback = () => {
  showFeedback.value = false
  emit('close')
  
  // Track dismissal
  selfImprovement.trackInteraction('feedback_dismissed', {
    hadRating: selectedRating.value > 0
  }, { dismissed: true })
}
</script>

<style scoped>
.feedback-collector {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: var(--surface-color, #1e1e1e);
  border: 1px solid var(--border-color, #333);
  border-radius: 12px;
  padding: 20px;
  max-width: 350px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.feedback-content {
  position: relative;
}

.feedback-content h4 {
  margin: 0 0 15px 0;
  color: var(--text-primary, #e0e0e0);
  font-size: 16px;
}

.rating-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.rating-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary, #888);
  transition: all 0.2s;
  padding: 5px;
}

.rating-btn:hover {
  transform: scale(1.2);
}

.rating-btn.active {
  color: var(--accent-color, #00ff9f);
}

.feedback-form textarea {
  width: 100%;
  background: var(--input-bg, #2a2a2a);
  border: 1px solid var(--border-color, #333);
  border-radius: 8px;
  padding: 10px;
  color: var(--text-primary, #e0e0e0);
  resize: none;
  font-family: inherit;
  margin-bottom: 10px;
}

.feedback-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.submit-btn,
.dismiss-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.submit-btn {
  background: var(--accent-color, #00ff9f);
  color: var(--background-color, #0a0a0a);
  font-weight: 500;
}

.submit-btn:hover {
  background: var(--accent-hover, #00cc7f);
}

.dismiss-btn {
  background: transparent;
  color: var(--text-secondary, #888);
  border: 1px solid var(--border-color, #333);
}

.dismiss-btn:hover {
  background: var(--surface-hover, #2a2a2a);
}

.close-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  background: var(--surface-color, #1e1e1e);
  border: 1px solid var(--border-color, #333);
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary, #888);
  font-size: 20px;
  line-height: 1;
}

.close-btn:hover {
  color: var(--text-primary, #e0e0e0);
  background: var(--surface-hover, #2a2a2a);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>