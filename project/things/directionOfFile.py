
def student_photo_upload(instance, filename):
    # file will be uploaded to MEDIA_ROOT/test/<filename>
    return 'students/{0}/{1}'.format(instance.student.id,filename)
def photo_upload(instance, filename):
    # file will be uploaded to MEDIA_ROOT/test/<filename>
    return 'students/{0}/{1}'.format(instance.id,filename)
