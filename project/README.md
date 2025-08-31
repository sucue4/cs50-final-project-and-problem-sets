# You vs AI: NBA draft
#### Video Demo:  [My Video Demo](https://youtu.be/-eNR6ktSaKc?si=r7uYNSc2HzJo-U4z)
#### Description:

### Personal Statement
I chose to make this project as when I was kid, I would use this website called 2kMTCentral where I could make a draft using cards from the gamemode MyTeam in NBA2k. I wanted to make a sort of draft like that, but with the real life stats of NBA players. I wanted to add a way for users to compete and replay the game, which is why I added a leaderboard and 10 NBA players per position to mix up the options per draft. I am fond of these games that utilize RNG and that was my motivation when thinking of what project I want to make.

This website allows the user to login (or register if they dont have a user yet) and track their wins. The user can draft a starting 5 with 3 options per position. They have to make sure to have a higher score than the AI's team. This can be done by choosing players with the best all-around stats. A leaderboard is also shown on the homepage to display the top 10 users with the most wins.

### Json and styles.css files explanation
The `players.json` file stores all the NBA player data used for the drafting and calculation of score. It includes ten players for each of the five positions and each player entry includes their name and points (PTS), rebounds (REB), and assists (AST). It also includes a URL to an image of the player, which is used to display players on the result pages. These player images are stored in the `/static/images` directory and are rendered using `<img>` tags in the HTML templates.
**The regular season stats and images for the players were taken from** [NBA.com](https://ph.global.nba.com/statistics/)

The `styles.css` file contains all the custom CSS that styles the website. It sets the overall layout and visual theme, including `#ffa500` or orange for the background color and centered page content. It uses sans-serif fonts for readability and applies specific styles to player photos, team sections, the leaderboard, and buttons. For example, code like `.circle-photo` and `.player-photo` round the player images, while `.player-card` adds borders and spacing. Flexbox is used in `.team-container` to align the player cards nicely. There are also hover effects and layout adjustments to ensure the site looks good on different screen sizes, making it more responsive. **ChatGPT was used to help me understand styling techniques such as Flexbox and to explore different layout options to improve the visual appeal of the website. I tested various settings and learned how to properly apply styles across different elements to find the combinations that worked best, espcially using bootstrap.**

### templates explanation
The `draft.html` template allows users to build their NBA starting five by selecting one player for each position. JavaScript is used to validate the form through the `validateForm()` function, which checks if all five positions are filled. If any dropdown is left empty, an alert appears saying “Please select a player for each position.” Jinja is used to dynamically generate the dropdowns with `{% for pos, players in draft_pool.items() %}` and to list each player’s name and stats using `{% for player in players %}`. When the form is submitted, the data is sent to the Flask server via a POST request, which processes the choices and calculates the result. The page uses styles.css for consistent styling across the app. **ChatGPT was used to help me better understand how to create my own JavaScript validation function and to improve the structure of my Jinja template code.**

The `index.html` file serves as the homepage of the NBA draft simulator. It includes a welcome message, the button to start the draft, a link to the official NBA website, and a leaderboard showing the top 10 registered users with the most wins. The user, while logged in, is shown their username and win count; otherwise, links to login or register are displayed. Jinja is used with `{% if username %}` to conditionally show content based on the user’s session, and `{% if leaderboard %}` to display the top 10 players dynamically. I used ChatGPT to help me understand how to properly incorporate Bootstrap and use styles.css to ensure the layout is clean  and visually appealing. I also used it to learn about styling utilities like `mb-3` and `mb-4` for managing spacing (margins).

`login.html` and `register.html` provide a way for users to securely create an account and sign in using their credentials. Each form sends a POST request to specific Flask routes which handle authentication and store user information in the SQLite database called `users.db`. Upon successfully registering or logging in, the user is redirected to the homepage.

`result.html` displays the outcome of the draft between the user and the AI. It shows the winner, each team's total score, and the full lineup for both the user and the AI. Player cards are dynamically generated using Jinja through `{% for pos, player in user_team.items() %}` and `{% for pos, player in ai_team.items() %}`, which include each player’s image, name, position, and stats. There is a "Back to Home" and the layout is styled with styles.css for visual consistency. ChatGPT was used here to help me understand and make sure that all the Jinja logic was working, especially in displaying the stats, player images, position, and scores. I found this a bit challenging when I first started making the file, but the tool helped me to troubleshoot and better understand how dynamic data rendering works in Flask.

### app.py explanation (Flask backend)
The `app.py` file serves as the backend logic for the NBA Draft Simulator website. It uses the Flask framework to manage routing, user authentication, session handling, and integration with a local SQLite database. Player data is loaded from a JSON file and used to power the draft functionality and scoring system.

Several libraries are imported to handle different tasks as seen at the start of the file. Flask helps handle web routing and rendering HTML templates, while `werkzeug.security` is used to hash and verify passwords securely. SQLite is also used to store and retrieve user data (such as usernames and win counts), and flask_session manages user sessions on the server. The json and random libraries are used to load the data for players and randomly pick a team for the AI respectively.

The app is configured with a secret key for session encryption and uses server-side sessions to keep users logged in across the different pages. A function called `get_db()` ensures the app connects to the users.db database when needed, and `close_db()` closes the connection after each request to avoid memory leaks. `get_db()` stores the connection to the database in a special flask variable called `g`, which stores data during a request.

Player data is preloaded from the players.json file, which contains information like name, position, stats, and image path for each player. The data is stored in a dictionary called all_players which is organized by position.

### User Authentication
- /register: Handles user sign-up. When a user submits a username and password, the password is hashed using `generate_password_hash()` and stored in the database with an initial win count of 0. If the username is already taken, it returns an error. The new user is inserted into the users table of the database. After successfully registering, the user is redirected to the login page.

- /login: This checks if the entered username exists and verifies the hashed password. If successful, it starts a session by saving the user’s ID and username. If the credentials are invalid, an error pops up.

- /logout: This clears the session and logs the user out. The logout button is seen on the top right of the homepage.

### Homepage and Leaderboard
The root route (/) displays the homepage. If a user is logged in, it retrieves their username and win count from the database. It also fetches the top 10 users with the most wins to display on the leaderboard using the code `leaderboard = db.execute( "SELECT username, wins FROM users ORDER BY wins DESC LIMIT 10").fetchall()`. All this information is passed to the index.html template for rendering.

### Drafting and Game Logic
The `/draft` route powers the core feature of the website, which is the drafting of the players and simulating a matchup. The user is asked to select a player using `request.form.get`. When a user submits their draft picks, the app builds their team using data from all_players. The code `draft_pool = {pos: random.sample(players, 3) for pos, players in all_players.items()}` is used to randomly select 3 players from the json file for the user to select. The AI team is randomly generated by selecting one player per position using the code `ai_team = {pos: random.choice(all_players[pos]) for pos in all_players}`.

A helper function called `calculate_score(team)` calculates the total score for both team by summing each player's points, rebounds, and assists. Based on the scores, the winner is determined with a simple comparison:

- If the user’s score is higher, the message is set to “You Win!” and increments the win count of the user in the database when a user is in session.

- If the scores are equal, it displays “It’s a Tie!”

- Otherwise, it shows “You Lose!”

The final result is rendered using result.html, which displays the full team lineups, scores, and the match outcome. If the user reloads the page or accesses the draft page without submitting a team, a new draft pool is generated by randomly sampling 3 players per position. This pool is then shown in the `draft.html` template so the user can build a team.

ChatGPT was used to help me implement werkzeug.security, troubleshoot errors, and understand how to properly structure the code, especially for the different Flask routes. It also supported me in adding extra features like login and registration, improving password security, and adding safeguards such as preventing duplicate usernames. I was able to discover and understand how werkzeug.security works through the use of this tool.
