# Movie Directory

## Table of Contents
1. Introduction
2. Features
3. Installation
4. Usage
5. Security

## Introduction
Welcome to the Movie Directory project! This is a comprehensive directory that provides detailed information about a wide range of movies. It's designed with a user-friendly interface and robust functionality to enhance your movie exploration experience.

## Features
Our Movie Directory offers a variety of features:

- **Movie Search**: Our powerful search functionality allows you to find movies by title quickly and accurately.
- **Detailed Information**: For each movie, we provide comprehensive information, including cast, director, genre, release date, runtime, and more.
- **User-Friendly Interface**: The interface is designed to be intuitive and easy to navigate, enhancing the user experience.
- **User Authentication**: Users can create an account and log in to access personalized features.
- **Password Recovery**: In case users forget their password, they can request a password reset link to be sent to their registered email address.

## Installation
Follow these steps to install the Movie Directory:

1. Clone the repository: `git clone https://github.com/AlexandruPanta/Movie-Directory.git`
2. Navigate to the project directory: `cd Movie-Directory`

## Usage
To use the Movie Directory:

1. Start the server: `python3 app.py`
2. After starting the server, open your web browser and navigate to `http://localhost:3000` to start exploring movies!

## Security
We take security seriously in our Movie Directory project:

- **Password Hashing**: User passwords are hashed using a secure hashing algorithm before being stored in our database. This means that even we don't know what your password is!

- **Email Verification**: When a user forgets their password, an email is sent with a secure link to reset their password.
