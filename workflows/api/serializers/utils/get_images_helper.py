def get_images_helper(request, images):
    """
    Helper method for gathering an object's list of images and formatting them along with their
    corresponding types.

    Parameters:
        request : Request object from the serializer instance.
        images : Queryset of image objects connected to the Object

    Returns:
        List of Image objects in JSON format.

    """
    image_list = []

    for image in images:
        image_dict = {
            "image_url": f"{request.scheme}://{request.get_host()}{image.image.url}",
            "image_type": image.type.type,
        }
        image_list.append(image_dict)

    return image_list
