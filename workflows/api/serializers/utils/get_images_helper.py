def get_images_helper(images):
    """
    Helper method for gathering an object's list of images and formatting them along with their
    corresponding types.

    Parameters:
    images: Queryset of image objects connected to the Object

    Returns:
        List of Image objects in JSON format.

    """
    image_list = []

    for image in images:
        image_dict = {
            "image_url": image.image.__str__(),  # TODO: Make this a hyperlink field
            "image_type": image.type.type
        }
        image_list.append(image_dict)

    return image_list
