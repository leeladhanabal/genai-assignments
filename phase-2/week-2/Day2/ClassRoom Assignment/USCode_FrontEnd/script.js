const WEBHOOK_URL = 'http://localhost:8001/api/review';

const storyKeyInput = document.getElementById('storyKey');
const reviewButton = document.getElementById('reviewButton');
const resultCopy = document.querySelector('.result-copy');

const resultPanel = document.querySelector('.result-panel');

const showResult = (message, status = 'neutral') => {
  resultCopy.textContent = message;
  resultPanel.classList.remove('loading', 'success', 'error');

  if (status === 'loading') {
    resultPanel.classList.add('loading');
    reviewButton.disabled = true;
    reviewButton.textContent = 'Reviewing...';
  } else {
    reviewButton.disabled = false;
    reviewButton.textContent = 'Review Story';
  }

  if (status === 'success') {
    resultPanel.classList.add('success');
    document.querySelector('.status-chip').textContent = 'Success';
  } else if (status === 'error') {
    resultPanel.classList.add('error');
    document.querySelector('.status-chip').textContent = 'Error';
  } else {
    document.querySelector('.status-chip').textContent = 'Waiting';
  }
};

const handleValidation = () => {
  const storyKey = storyKeyInput.value.trim();
  if (!storyKey) {
    showResult('Please enter a Jira Story Key before reviewing.', 'error');
    return false;
  }
  return true;
};

const fetchReview = async (storyKey) => {
  showResult('Generating AI review... Please wait.', 'loading');

  try {
    const response = await fetch(WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ storyKey }),
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    const reviewText = data.review || data.message || JSON.stringify(data);
    showResult(reviewText, 'success');
  } catch (error) {
    showResult('Unable to fetch the review. Please try again later.', 'error');
    console.error('Review fetch error:', error);
  }
};

reviewButton.addEventListener('click', () => {
  if (!handleValidation()) {
    return;
  }

  fetchReview(storyKeyInput.value.trim());
});
