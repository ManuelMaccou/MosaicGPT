function getCurrentPath() {
  const pathName = window.location.pathname;
  console.log("Current path:", pathName);
  if (pathName.includes('PYMNTS')) {
      return 'PYMNTS';
  } else if (pathName.includes('Bankless')) {
      return 'Bankless';
  } else {
      // Handle the case where the path is neither
      console.error('Invalid path');
      return null;
  }
}

function setBranding() {
  const currentPath = getCurrentPath();
  let logoHeader, logoLanding, primaryColor, secondaryColor, primaryTextColor, secondaryTextColor, landingHeader, questionSuggestion1, questionSuggestion2, questionSuggestion3, questionSuggestion4, feedbackLink;

  if (currentPath === 'PYMNTS') {
      logoHeader = 'Logos/PYMNTS/PYMNTS_2023_logo_white.svg';
      logoLanding = 'Logos/PYMNTS/PYMNTS_2022_logo_medium_green.svg';
      primaryColor = '#FFFFFF';
      secondaryColor = '#00A469';
      primaryTextColor = '#000000';
      secondaryTextColor = '#FFFFFF';
      landingHeader = 'Explore the world of Payments';
      questionSuggestion1 = "How can we improve our risk management for digital currencies?";
      questionSuggestion2 = "What's the best way to integrate blockchain into our payment systems?";
      questionSuggestion3 = "Which international markets are ideal for financial expansion now?";
      questionSuggestion4 = "How do we add ESG criteria into our investment decisions?";
      feedbackLink = 'https://forms.gle/RaY8EfdZtBMPv3fZ7'
  } else if (currentPath === 'Bankless') {
      logoHeader = 'Logos/Bankless/bankless_icon.png';
      logoLanding = 'Logos/Bankless/bankless_icon.png';
      primaryColor = '#000000';
      secondaryColor = '#EB212D';
      primaryTextColor = '#FFFFFF';
      secondaryTextColor = '#FFFFFF';
      landingHeader = 'Explore web3 with Bankless';
      questionSuggestion1 = "What is the latest news in crypto?";
      questionSuggestion2 = "What are some investment opportunities in the current market?";
      questionSuggestion3 = "What challenges is OpenSea facing?";
      questionSuggestion4 = "How does Vitalik feel about AI?";
      feedbackLink = 'https://t.me/+QyptfCagmwRjMmEx'
  }

  // Set logos
  document.querySelector('.header-logo').src = '/static/' + logoHeader;
  document.querySelector('.landing-logo').src = '/static/' + logoLanding;

  // Set landing h1
  document.querySelector('.landing h1').textContent = landingHeader;

  // Set suggesetion questions
  document.getElementById('suggestion1m').textContent = questionSuggestion1;
  document.getElementById('suggestion2m').textContent = questionSuggestion2;
  document.getElementById('suggestion3m').textContent = questionSuggestion3;
  document.getElementById('suggestion4m').textContent = questionSuggestion4;
  document.getElementById('suggestion1').textContent = questionSuggestion1;
  document.getElementById('suggestion2').textContent = questionSuggestion2;
  document.getElementById('suggestion3').textContent = questionSuggestion3;
  document.getElementById('suggestion4').textContent = questionSuggestion4;

  // Set feedback link
  document.getElementById('feedback').href = feedbackLink;
  document.getElementById('feedbackm').href = feedbackLink;

  // Set CSS variables for colors
  document.documentElement.style.setProperty('--primary-color', primaryColor);
  document.documentElement.style.setProperty('--secondary-color', secondaryColor);
  document.documentElement.style.setProperty('--primary-text-color', primaryTextColor);
  document.documentElement.style.setProperty('--secondary-text-color', secondaryTextColor);
}

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
  var closeMobileMenu = document.querySelector('.close-button');

  setBranding();

  fetch('/page-visit', { method: 'POST' })
    .then(response => response.json())
    .then(text => {
      console.log("Received response:", text);
    })
    .then(data => {
        console.log('API Response:', data);
    })
    .catch(error => {
        console.error('Error making the API call:', error);
    });
  
  if (!getCookie('firstVisit')) {
    showPopup();
    setCookie('firstVisit', '1', 7); // Expires in 7 days
  }

  function adjustHeight() {
    var vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
  }
  
  window.addEventListener('resize', adjustHeight);
  window.addEventListener('load', adjustHeight);
  
  adjustHeight();

  function showPopup() {
    document.getElementById('welcome-popup').style.display = 'flex';
    document.getElementById('overlay').style.display = 'block';
  }

  function closePopup() {
    document.getElementById('welcome-popup').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
  }

  var closeButton = document.querySelector('.welcome-popup-button');
    if (closeButton) {
      closeButton.addEventListener('click', closePopup);
  }
  
  function setCookie(name, value, days) {
    var expires = '';
    if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + (value || '') + expires + '; path=/';
  }
  
  function getCookie(name) {
    var nameEQ = name + '=';
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  }

  function sendDataToGptStats(query, elasticSearchSources) {
    fetch('/gpt-stats', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            question: query,
            sources_title: elasticSearchSources.map(source => source.title).join(', '),
            sources_url: elasticSearchSources.map(source => source.url).join(', ')
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('GPT Stats API Response:', data);
    })
    .catch(error => {
        console.error('Error making the GPT Stats API call:', error);
    });
  };

  menuButton.addEventListener('click', function() {
      mobileMenu.classList.toggle('visible');
  });
  closeMobileMenu.addEventListener('click', function() {
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

    let elasticSearchSources = [];

    // Establish connection to the server for streaming responses
    var currentPath = getCurrentPath();
    if (!currentPath) {
        console.error('No valid path found for the search.');
        return; // Exit the function if the path is not valid
    }

    var stream = new EventSource('/' + currentPath + '/search?query=' + encodeURIComponent(query));

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
        elasticSearchSources = sourceCards.map(card => ({ title: card.title, url: card.articleUrl }));
    
        if (sourceCards.length > 0) {
          sendDataToGptStats(query, elasticSearchSources);
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

