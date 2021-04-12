def get_images_helper(self, images):
    """
    Helper method for gathering an object's list of images and formatting them along with their
    corresponding types.

    Parameters:
        self : Instance of the Model Serializer
        images : Queryset of image objects connected to the Object

    Returns:
        List of Image objects in JSON format.

    """
    image_list = []

    request = self.context.get("request")

    for image in images:
        image_dict = {
            "image_url": f"{request.scheme}://{request.get_host()}{image.image.url}",
            "image_type": image.type.type
        }
        image_list.append(image_dict)

    return image_list
