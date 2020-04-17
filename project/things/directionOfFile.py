def images_upload(instance, filename):
    # file will be uploaded to MEDIA_ROOT/test/<filename>
    return 'media/test/{1}'.format(instance.number, filename)
def student_photo_upload(instance, filename):
    # file will be uploaded to MEDIA_ROOT/test/<filename>
    return 'student/{0}'.format(filename)
