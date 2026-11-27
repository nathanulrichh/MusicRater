# MusicRater

MusicRater is a full-stack music rating and discovery web application built using Python, Flask and MySQL. The application allows users to explore artists, albums and tracks, submit album ratings and manage music records through an interactive web interface.

Developed as part of CSE 385 at Miami University, this project emphasizes relational database design, data management and full-stack development.

## Features

- Browse and search artists, albums and tracks
- Submit and view album ratings
- Add, edit and manage database records
- Display album cover art and release dates
- Expand album listings to view individual tracks
- Search and sort music records
- Manage user information

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend application logic |
| Flask | Web application framework |
| MySQL | Relational database management |
| SQL | Data retrieval and manipulation |
| HTML | Web page structure |
| CSS | User interface styling |
| JavaScript | Interactive interface components |
| Jinja2 | Dynamic HTML templating |
| MySQL Connector | Database connectivity |
| Git/GitHub | Version control and collaboration |

## Database Design

MusicRater utilizes a relational MySQL database designed around Third Normal Form (3NF) to minimize data redundancy and maintain data integrity.

### Database Entities

- Users
- Artists
- Albums
- Songs
- Album Ratings

### Database Concepts

- Primary and foreign keys
- Relational database normalization (1NF, 2NF, 3NF)
- Referential integrity
- SQL joins and aggregation
- Parameterized SQL queries
- CRUD operations
- Database connection pooling
- One-to-many relationships

## Application Architecture

MusicRater follows a three-tier application architecture:

| Layer | Technologies | Responsibility |
|---|---|---|
| Presentation | HTML, CSS, JavaScript, Jinja2 | User interface |
| Application | Python, Flask | Backend logic and routing |
| Data | MySQL, SQL | Data storage and management |

## Getting Started

### Prerequisites

- Python 3
- MySQL 8.0
- Git
- pip

### Installation

1. Clone the repository.

2. Install the required dependencies:

   ```bash
   pip install flask mysql-connector-python
   ```

3. Create the MySQL database using the database schema provided in the repository.

4. Populate the database with the provided sample data.

5. Configure the database connection using the appropriate environment variables.

6. Start the Flask application.

   ```bash
   flask run
   ```

7. Open the application in your browser.

   ```
   http://127.0.0.1:5000
   ```

## Project Objectives

- Design and implement a normalized relational database
- Develop a functional full-stack web application
- Implement efficient SQL queries for data retrieval and manipulation
- Maintain data consistency and referential integrity
- Provide an intuitive interface for interacting with relational data
- Gain practical experience with database-driven software development

## Future Improvements

- [ ] External music API integration
- [ ] Personalized music recommendation system
- [ ] Advanced search and filtering
- [ ] User listening profiles and rating histories
- [ ] Album and artist popularity rankings
- [ ] Interactive data visualization dashboards
- [ ] Statistical analysis of user rating patterns
- [ ] Machine learning-based music recommendations

## Academic Context

This application was developed as a collaborative final project for CSE 385: Database Systems at Miami University.

The project combines relational database modeling, SQL programming, database management and full-stack software development into a single functional application.

