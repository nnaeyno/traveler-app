
# Traveler App - RoadRunner

Roadrunner is a travel helper app designed to simplify trip planning for individuals or groups. 
The app provides users with a personal "workspace" where they can collaborate with friends, 
track travel documents, plan destinations on a map, and manage their packing list. The application 
integrates a variety of features, including real-time communication, document storage, and mapping 
functionalities.

## Features
* User Authentication:
  * Users authenticate via JWT tokens, ensuring secure access to their travel workspace. This allows users to have their own private space while enabling collaboration.

* Workspace (also known as City):
  * Users have access to a dedicated workspace/trip for each trip where they can interact with other trip members, plan destinations, and share travel information.

* Interactive Map:
  * Integration with Leaflet Maps API allows users to place pins on the map representing destinations they'd like to visit. When a pin is clicked, users can engage in live discussions, rating, or leaving notes about that location.

* Real-time Notifications:
  * Notifications are sent via Django Celery, ensuring users are alerted for important events like new comments.


* Luggage Checklist:
  * Users can create and manage a checklist of items to pack, ensuring they never forget important items for their trips.

* Travel Documents:
  * A separate section for storing and managing all travel-related documents such as flight tickets, hotel bookings, and other essential travel papers.


* Swagger API Documentation:
  * The app includes a full API for backend functionality built with Django Rest Framework. Swagger is integrated for easy exploration and testing of the API endpoints.

* Caching:
  * Performance is enhanced by caching, which reduces redundant database queries and accelerates data loading in frequently accessed components.

* Frontend Integration:
  * The frontend is implemented using Django templates, forms, and web components. JavaScript is utilized for dynamic behavior such as live chat and interactive map updates.

## Technologies Used
### Backend:

* Django
* Django Rest Framework (DRF)
* JWT Authentication
* Django Celery for asynchronous task processing
* Django Caching

### Frontend:

* Django Templates
* Django Forms
* Leaflet Maps API
* JavaScript (for dynamic interactions)

### API Documentation:

* Swagger UI for interactive API documentation

### Database:

* Complex database models including relationships for users, places, cities, documents, and more


# Future enhancements

* Front end for Luggage app, User profile, City pages
* Allow messaging between users
* Change for Google Maps API 
* Deployment (AWS)


### additional Requirements

_install django-leaflet as well as gdal (brew install gdal pip install gdal)
and allow location permissions from your browser_

### notes

**_THIS IS MAINLY A BACKEND PROJECT, FRONT IS DONE PARTIALLY. FOR REGISTRATION USE `/api/register/` ENDPOINT
DB IS INCLUDED IN THE REPO FOR TESTING PURPOSES AND DATA IS TESTING DATA_** 