document.addEventListener('DOMContentLoaded', function() {
  var menuButton = document.querySelector('.menu-button');
  var mobileMenu = document.querySelector('.mobile-menu');
  var searchInput = document.getElementById('searchQuery');
  var searchButton = document.querySelector('.search-button');
  var suggestionButtons = document.querySelectorAll('.suggestion-button');
  var sourceColumn = document.getElementById('sourceColumn');
  var sourceMobileContainer = document.getElementById('sourceMobileContainer');
  var tempLanding = document.getElementById('tempLanding');
  var answerContainer = document.getElementById('answerContainer');
  var closeButton = document.querySelector('.close-button');

  menuButton.addEventListener('click', function() {
      mobileMenu.classList.toggle('visible');
  });
  closeButton.addEventListener('click', function() {
    mobileMenu.classList.remove('visible');
  });

  suggestionButtons.forEach(button => {
    button.addEventListener('click', function() {
        searchInput.value = this.textContent; // Set the search input value to the button's text
        searchButton.click(); // Programmatically click the search button

        mobileMenu.classList.remove('visible');
    });
});

  searchInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent the default action to avoid form submission
        searchButton.click(); // Trigger the search button click programmatically
    }
  });  

  document.querySelector('.search-button').addEventListener('click', function(event) {
    event.preventDefault();
    var query = document.getElementById('searchQuery').value;

    document.getElementById('spinner').style.display = 'block';

    // Clear existing content
    answerContainer.innerHTML = '';
    sourceColumn.innerHTML = '';
    sourceMobileContainer.innerHTML = '';

    // Establish connection to the server for streaming responses
    var stream = new EventSource('/search?query=' + encodeURIComponent(query));
    var receivedSourceCards = false;

    let accumulatedContent = "";

    // Listen for when the stream is successfully opened
    stream.onopen = function(event) {
      console.log('Stream opened successfully:', event);
    };

    // Listen for messages from the server
    stream.onmessage = function(event) {
      if (!receivedSourceCards) {
        var sourceCards = JSON.parse(event.data);
    
        if (sourceCards.length > 0) {
          tempLanding.style.display = 'none';
    
          sourceCards.forEach(function(card) {
            var cardElement = document.createElement('div');
            cardElement.className = 'source-card';
          
            var cardLink = document.createElement('a');
            cardLink.href = card.articleUrl;
            cardLink.target = '_blank';
            cardLink.className = 'card-link';
    
            cardLink.innerHTML = `
              <img src="${card.image}" alt="${card.title}">
              <h3 class="source-text">${card.title}</h3>
            `;
    
            cardElement.appendChild(cardLink);

            var destinationContainer = window.innerWidth <= 768 ? 
              document.getElementById('sourceMobileContainer') :
              document.getElementById('sourceColumn');

            destinationContainer.appendChild(cardElement);
          });

          receivedSourceCards = true;
        }
      } else {
        accumulatedContent += event.data;
        answerContainer.innerHTML = accumulatedContent;
      }
      document.getElementById('spinner').style.display = 'none';
    };

    stream.onerror = function(error) {
      console.error('Stream Error:', error);
      document.getElementById('spinner').style.display = 'none';
      if (event.target && event.target.readyState === EventSource.CLOSED) {
        console.log('Stream Closed');
      }
      stream.close(); // Close the stream on error
    };
    searchInput.value = '';
  });
});

