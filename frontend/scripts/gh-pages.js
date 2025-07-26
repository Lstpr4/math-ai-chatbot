// Simple static data fetcher for GitHub Pages version
document.addEventListener('DOMContentLoaded', function() {
  // Show note about static version
  const staticNoteDiv = document.createElement('div');
  staticNoteDiv.className = 'static-note';
  staticNoteDiv.innerHTML = `
    <div class="alert">
      <p><strong>Note:</strong> You're viewing the static GitHub Pages version of Mathly.</p>
      <p>For full functionality including API calls, please run the app locally.</p>
      <p><a href="https://github.com/Lstpr4/math-ai-chatbot" target="_blank">Get the full version on GitHub</a></p>
    </div>
  `;
  
  document.body.insertBefore(staticNoteDiv, document.body.firstChild);
  
  // Add CSS for the static note
  const style = document.createElement('style');
  style.textContent = `
    .static-note {
      position: fixed;
      top: 10px;
      left: 10px;
      z-index: 1000;
      width: 300px;
    }
    
    .alert {
      background-color: rgba(255, 255, 255, 0.9);
      border-left: 4px solid #ff9800;
      padding: 12px;
      border-radius: 4px;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
      font-size: 14px;
      line-height: 1.4;
    }
    
    .alert a {
      color: #0066cc;
      text-decoration: none;
      font-weight: bold;
    }
    
    .alert a:hover {
      text-decoration: underline;
    }
  `;
  
  document.head.appendChild(style);
});
