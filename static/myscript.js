 // defining the function for submiting the form when a category was selected
function submitForm() {
    document.getElementById("categoryProductsForm").submit();       
}


document.addEventListener("DOMContentLoaded", function () {
    // code for displaying the enlarged images when the user clicks the search button from the menu-images
    document.querySelectorAll('.menu-portofolio .zoom-button').forEach(image => {
        image.onclick = (event) => {
            event.stopPropagation(); // prevent the click event from propagating
            const parentContainer = image.closest('.image-product');
            const imageElement = parentContainer.querySelector('.menu-images');
            const clickedImageSrc = imageElement.getAttribute('src');

            document.querySelector('.enlargeImage').style.display = 'block';
            document.querySelector('.enlargeImage img').src = clickedImageSrc;
        }
    });
    document.querySelector('.close-enlargedImg').onclick = () => {
        document.querySelector('.enlargeImage').style.display = 'none';
    }
    // event listener for when the user clicks outside the enlarged image
    document.addEventListener('click', function (event) {
        if (!event.target.closest('.enlargeImage')) {
            document.querySelector('.enlargeImage').style.display = 'none';
        }
    });   
});