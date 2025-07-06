document.addEventListener('DOMContentLoaded', () => {
    const loginBtn = document.querySelector('.login-btn');
    const usernameInput = document.querySelector('input[placeholder="Enter your username"]');
    const passwordInput = document.querySelector('input[placeholder="Enter your password"]');
  
    loginBtn.addEventListener('click', (e) => {
      e.preventDefault(); // Prevent form default behavior
  
      const username = usernameInput.value.trim();
      const password = passwordInput.value.trim();
  
      if (!username || !password) {
        alert('Please enter both username and password.');
        return;
      }
  
      // Send data to backend using fetch (optional if you build an API)
      fetch('/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          window.location.href = '/'; // redirect to homepage
        } else {
          alert(data.message || 'Login failed.');
        }
      })
      .catch(err => {
        console.error('Login error:', err);
        alert('Something went wrong.');
      });
    });
  });
  