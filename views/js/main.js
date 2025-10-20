// This file contains the JavaScript code for the application.
// It displays a "Hello, World!" message in the console and manipulates the DOM.

document.addEventListener('DOMContentLoaded', function() {
    // Create a new paragraph element
    const helloWorldParagraph = document.createElement('p');
    // Set the text content to "Hello, World!"
    helloWorldParagraph.textContent = 'Hello, World!';
    // Append the paragraph to the body of the document
    document.body.appendChild(helloWorldParagraph);
    
    // Log the message to the console
    console.log('Hello, World!');
});