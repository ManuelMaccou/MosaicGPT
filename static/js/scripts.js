function getCurrentPath() {
  const pathName = window.location.pathname.toLowerCase();
  if (pathName.includes('pymnts')) {
        return 'PYMNTS';
    } else if (pathName.includes('finance')) {
        return 'Finance';
    } else if (pathName.includes('bankless')) {
        return 'Bankless';
    } else if (pathName.includes('polkadot')) {
      return 'Polkadot';
    } else if (pathName.includes('linea')) {
      return 'Linea';
    } else if (pathName.includes('celo')) {
      return 'Celo';
    } else if (pathName.includes('stacks')) {
      return 'Stacks';
    } else if (pathName.includes('rootstock')) {
      return 'Rootstock';
    } else {
        console.error('Invalid path');
        return null;
    }
}

function setBranding() {
  const currentPath = getCurrentPath();
  let logoHeader, logoLanding, primaryColor, secondaryColor, primaryTextColor, secondaryTextColor, landingHeader, questionSuggestion1, questionSuggestion2, questionSuggestion3, questionSuggestion4, feedbackLink, welcomePopupTitle, welcomePopupText, recentArticlesQuery = null;

  const recentArticlesButtons = document.querySelectorAll('.recent-articles-button');
  recentArticlesButtons.forEach(button => {
    if (currentPath === 'PYMNTS' || currentPath === 'Bankless') {
      button.style.display = 'block';
    } else {
      button.style.display = 'none';
    }
  });

  const suggestion4Button = document.querySelectorAll('.suggestion-button-4');
  suggestion4Button.forEach(button => {
    if (currentPath === 'PYMNTS' || currentPath === 'Bankless') {
      button.style.display = 'none';
    } else {
      button.style.display = 'block';
    }
  });

  if (currentPath === 'PYMNTS') {
    logoHeader = 'Logos/PYMNTS/PYMNTS_2023_logo_white.svg';
    headerColor = '#000000';
    logoLanding = 'Logos/PYMNTS/PYMNTS_2022_logo_medium_green.svg';
    primaryColor = '#FFFFFF';
    secondaryColor = '#00A469';
    primaryTextColor = '#000000';
    secondaryTextColor = '#FFFFFF';
    landingHeader = 'Explore the world of Payments';
    recentArticlesQuery = "What is the latest news from PYMNTS?";
    questionSuggestion1 = "How can we improve our risk management for digital currencies?";
    questionSuggestion2 = "Which international markets are ideal for financial expansion now?";
    questionSuggestion3 = "How do we add ESG criteria into our investment decisions?";
    feedbackLink = 'https://forms.gle/RaY8EfdZtBMPv3fZ7';
    welcomePopupTitle = "PYMNTS GPT Demo";
    welcomePopupText = "This is a simple demo to provide an early idea of what an AI assistant could provide the PYMNTS community. We invite you to try it out and let us know what you think. This demo was made by the Mosaic team for demo purposes only and is not affiliated with PYMNTS in any way. We may retain questions asked in this demo to better understand what the community is interested in learning. Do not share any personal information.";
  } else if (currentPath === 'Finance') {
    logoHeader = 'Logos/mosiac_logo_horizontal.png';
    headerColor = '#FFFFFF';
    logoLanding = 'Logos/mosiac_logo_.png';
    primaryColor = '#FFFFFF';
    secondaryColor = '#0d0e24';
    primaryTextColor = '#2d2d2d';
    secondaryTextColor = '#2d2d2d';
    landingHeader = 'Explore the world of finance';
    questionSuggestion1 = "What are some investment opportunities in the current market?";
    questionSuggestion2 = "How do emerging market dynamics affect global financial stability?";
    questionSuggestion3 = "How are financial institutions using blockchain technology?";
    questionSuggestion4 = "How are financial institutions using AI?";
    feedbackLink = 'https://forms.gle/33bv5dPpQ4hQGS4U9';
    welcomePopupTitle = "A custom GPT for finance";
    welcomePopupText = "Thank you for checking out this early version of a custom GPT built specifically for the finance industry. If you haven't joined out LinkedIn group, you can do so below. If you're a writer or journalist, you can contribute your content to be included in the GPT. In order to learn what the finance community is interested in learning, we may save the questions you ask. No personal information will be stored. DO NOT SHARE ANY PERSONAL INFORMATION. We will take your feedback to make this GPT more useful.";
  } else if (currentPath === 'Celo') {
    logoHeader = 'Logos/Celo/Celo_Symbol_RGB_Onyx.png';
    headerColor = '#FBF6F1';
    logoLanding = 'Logos/Celo/Celo_Wordmark_RGB_Onyx.png';
    primaryColor = '#FBF6F1';
    secondaryColor = '#1A0329';
    primaryTextColor = '#2d2d2d';
    secondaryTextColor = '#2d2d2d';
    landingHeader = 'Explore the world of Celo';
    questionSuggestion1 = "How to I build on Celo with Remix?";
    questionSuggestion2 = "How do I run a validator?";
    questionSuggestion3 = "How is Celo different from other blockchains?";
    questionSuggestion4 = "What is the easiest way to get started building on Celo?";
    feedbackLink = 'https://t.me/+QyptfCagmwRjMmEx';
    welcomePopupTitle = "Welcome to Celo GPT";
    welcomePopupText = "This is a basic demo of an AI assistant with knowledge of all things Celo. This was created by the team at Mosaic, and does not have any official affiliation with Celo. The purpose of this demo is to learn what the world of crypto is interested in learning, so we may save the questions you ask. DO NOT SHARE ANY PERSONAL INFORMATION. We will take your feedback to make this GPT more useful.";
  } else if (currentPath === 'Stacks') {
    logoHeader = 'Logos/Stacks/nexus-circle-dark-theme.png';
    headerColor = '#FFFFFF';
    logoLanding = 'Logos/Stacks/stacks-light-theme.png';
    primaryColor = '#FFFFFF';
    secondaryColor = '#000000';
    primaryTextColor = '#2d2d2d';
    secondaryTextColor = '#2d2d2d';
    landingHeader = 'Explore the world of Stacks';
    questionSuggestion1 = "How does Stacks bring DeFi to Bitcoin?";
    questionSuggestion2 = "What consensus mechanism does Stacks use?";
    questionSuggestion3 = "What are the mining rewards?";
    questionSuggestion4 = "How do I get started building on Stacks?";
    feedbackLink = 'https://t.me/+QyptfCagmwRjMmEx';
    welcomePopupTitle = "Welcome to Stacks GPT";
    welcomePopupText = "This is a basic demo of an AI assistant with knowledge of all things Stacks. This was created by the team at Mosaic, and does not have any official affiliation with Stacks. The purpose of this demo is to learn what the world of crypto is interested in learning, so we may save the questions you ask. DO NOT SHARE ANY PERSONAL INFORMATION. We will take your feedback to make this GPT more useful.";
  } else if (currentPath === 'Rootstock') {
    logoHeader = 'Logos/Rootstock/rootstock_icon_white.png';
    headerColor = '#000000';
    logoLanding = 'Logos/Rootstock/rootstock_logo_black.png';
    primaryColor = '#FFFFFF';
    secondaryColor = '#FF9002';
    primaryTextColor = '#000000';
    secondaryTextColor = '#000000';
    landingHeader = 'Explore the world of Rootstock';
    questionSuggestion1 = "How does Rootstock bring DeFi to Bitcoin?";
    questionSuggestion2 = "What is the Flyover protocol and how does it work?";
    questionSuggestion3 = "How do I deploy an NFT on Rootstock";
    questionSuggestion4 = "How do I get started building on Rootstock?";
    feedbackLink = 'https://t.me/+QyptfCagmwRjMmEx';
    welcomePopupTitle = "Welcome to Rootstock GPT";
    welcomePopupText = "This is a basic demo of an AI assistant with knowledge of all things Rootstock. This was created by the team at Mosaic, and does not have any official affiliation with Rootstock. The purpose of this demo is to learn what the world of crypto is interested in learning, so we may save the questions you ask. DO NOT SHARE ANY PERSONAL INFORMATION. We will take your feedback to make this GPT more useful.";
  } else if (currentPath === 'Bankless') {
    logoHeader = 'Logos/Bankless/bankless_icon.png';
    headerColor = '#000000';
    logoLanding = 'Logos/Bankless/bankless_icon.png';
    primaryColor = '#000000';
    secondaryColor = '#EB212D';
    primaryTextColor = '#FFFFFF';
    secondaryTextColor = '#FFFFFF';
    landingHeader = 'Explore web3 with Bankless';
    recentArticlesQuery = "What is the latest news in crypto?";
    questionSuggestion1 = "What are some investment opportunities in the current market?";
    questionSuggestion2 = "What challenges is OpenSea facing?";
    questionSuggestion3 = "How does Vitalik feel about AI?";
    feedbackLink = 'https://t.me/+QyptfCagmwRjMmEx'
    welcomePopupTitle = "BanklessGPT Demo"
    welcomePopupText = "This is a basic demo of an AI assistant with knowledge of all things Bankless. This was created by the team at Mosaic, and does not have any official affiliation with Bankless. The purpose of this demo is to learn what the world of crypto is interested in learning, so we may save the questions you ask. DO NOT SHARE ANY PERSONAL INFORMATION. We will take your feedback to make this GPT more useful.";
  } else if (currentPath === 'Polkadot') {
    logoHeader = 'Logos/Polkadot/Polkadot_Logo_Horizontal_Pink_White.png';
    headerColor = '#140523';
    logoLanding = 'Logos/Polkadot/Polkadot_Logo_Horizontal_Pink_White.png';
    primaryColor = '#140523';
    secondaryColor = '#E6007A';
    primaryTextColor = '#FFFFFF';
    secondaryTextColor = '#FFFFFF';
    landingHeader = 'Explore the Polkadot ecosystem';
    questionSuggestion1 = "What is the difference between Polkadot and Ethereum?";
    questionSuggestion2 = "What are some liquid staking apps on Polkadot?";
    questionSuggestion3 = "What are parachains and how do they work?";
    questionSuggestion4 = "Describe the Polkadot architecture";
    feedbackLink = 'https://t.me/+QyptfCagmwRjMmEx';
    welcomePopupTitle = "PolkadotGPT";
    welcomePopupText = "This is a basic demo of an AI assistant with knowledge of all things Polkadot. This was created by the team at Mosaic, and does not have any official affiliation with Polkadot. The purpose of this demo is to learn what the world of crypto is interested in learning, so we may save the questions you ask. DO NOT SHARE ANY PERSONAL INFORMATION. We will take your feedback to make this GPT more useful.";
  } else if (currentPath === 'Linea') {
    logoHeader = 'Logos/Linea/Logomark Black BG.png';
    headerColor = '#000000';
    logoLanding = 'Logos/Linea/Wordmark Black BG.png';
    primaryColor = '#000000';
    secondaryColor = '#62DFFF';
    primaryTextColor = '#FFFFFF';
    secondaryTextColor = '#FFFFFF';
    landingHeader = 'Explore the Linea ecosystem';
    questionSuggestion1 = "What is a zkEVM?";
    questionSuggestion2 = "What use cases are good fits for zero knowledge tech?";
    questionSuggestion3 = "How do you run a Linea node?";
    questionSuggestion4 = "How do gas fees work on Linea?";
    feedbackLink = 'https://t.me/+QyptfCagmwRjMmEx';
    welcomePopupTitle = "LineaGPT";
    welcomePopupText = "This is a basic demo of an AI assistant with knowledge of all things Linea. This was created by the team at Mosaic, and does not have any official affiliation with Linea. The purpose of this demo is to learn what the world of crypto is interested in learning, so we may save the questions you ask. DO NOT SHARE ANY PERSONAL INFORMATION. We will take your feedback to make this GPT more useful.";
  }

  // Set logos
  document.querySelector('.header-logo').src = '/static/' + logoHeader;
  document.querySelector('.landing-logo').src = '/static/' + logoLanding;

  // Set Welcome Popup
  document.querySelector('.popup-content h2').textContent = welcomePopupTitle;
  document.querySelector('.popup-content p').textContent = welcomePopupText;


  // Set landing h1
  document.querySelector('.landing h1').textContent = landingHeader;

  // Set suggeseted questions
  if (recentArticlesQuery) {
    document.getElementById('recentArticlesm').textContent = recentArticlesQuery;
    document.getElementById('recentArticles').textContent = recentArticlesQuery;
  }
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
  document.documentElement.style.setProperty('--header-color', headerColor);
}

document.addEventListener('DOMContentLoaded', function() {
  var menuButton = document.querySelector('.menu-button');
  var mobileMenu = document.querySelector('.mobile-menu');
  var searchInput = document.getElementById('searchQuery');
  var searchButton = document.querySelector('.search-button');
  var suggestionButtons = document.querySelectorAll('.suggestion-button');
  var suggestionButton4 = document.querySelectorAll('.suggestion-button-4');
  var sourceColumn = document.getElementById('sourceColumn');
  var sourceMobileContainer = document.getElementById('sourceMobileContainer');
  var tempLanding = document.getElementById('tempLanding');
  var answerContainer = document.getElementById('answerContainer');
  var closeMobileMenu = document.querySelector('.close-button');

  var closeButton = document.querySelector('.welcome-popup-button');
    if (closeButton) {
      closeButton.addEventListener('click', closePopup);
  }

  var recentArticlesClicked = false;
  var recentArticlesButtons = document.querySelectorAll('.recent-articles-button');
  recentArticlesButtons.forEach(button => {
    button.addEventListener('click', function() {
      recentArticlesClicked = true;
      // handleRecentArticlesClick();
    });
  });

  var currentPath = getCurrentPath();
  var cookieNameSuffix = currentPath ? '_' + currentPath : '';
  if (!getCookie('firstVisit', cookieNameSuffix)) {
    showPopup();
    setCookie('firstVisit', '1', 7, cookieNameSuffix); // Expires in 7 days
  }

  setBranding();

  fetch('/page-visit', { method: 'POST' })  
    .then(response => response.json())
    .catch(error => {
        console.error('Error making the API call:', error);
    });

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
  
  function setCookie(name, value, days, pathSuffix) {
    var expires = '';
    if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + pathSuffix + '=' + (value || '') + expires + '; path=/';
  }
  
  function getCookie(name, pathSuffix) {
    var nameEQ = name + pathSuffix + '=';
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  }

  function sendDataToGptStats(query, elasticSearchSources) {
    const currentPath = window.location.pathname;
    fetch('/gpt-stats', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            question: query,
            sources_title: elasticSearchSources.map(source => source.title).join(', '),
            sources_url: elasticSearchSources.map(source => source.url).join(', '),
            path: currentPath
        })
    })
    .then(response => response.json())
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

suggestionButton4.forEach(button => {
  button.addEventListener('click', function() {
      searchInput.value = this.textContent; // Set the search input value to the button's text
      searchButton.click(); // Programmatically click the search button

      mobileMenu.classList.remove('visible');
  });
});

recentArticlesButtons.forEach(button => {
  button.addEventListener('click', function() {
      // searchInput.value = this.textContent; // Set the search input value to the button's text
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

    if (recentArticlesClicked) {
      var numRecentArticles = currentPath === 'PYMNTS' ? 20 : currentPath === 'Bankless' ? 10 : null;
      if (!numRecentArticles) {
          console.error('Recent articles button not supported for this path');
          return;
      }
      var stream = new EventSource('/' + currentPath + '/recent-articles-search?num_recent_articles=' + numRecentArticles)
      recentArticlesClicked = false; // Reset the flag
    } else {
      var stream = new EventSource('/' + currentPath + '/search?query=' + encodeURIComponent(query));
    }

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

          suggestionButtons.forEach(function(button) {
            button.style.display = 'none';
          });

          suggestionButton4.forEach(function(button) {
            button.style.display = 'none';
          });

          recentArticlesButtons.forEach(function(button) {
            button.style.display = 'none';
          });
    
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

