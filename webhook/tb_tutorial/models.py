from django.db import models

# Create your models here.


class States:
    default = 'default'
    get_link = 'get_link'
    get_doc_id = 'get_doc_id'
    get_address = 'get_address'
    edit = 'edit'
    get_real_name = 'get_real_name'
    edit_tags = 'edit_tags'
    get_page_name = 'get_page_name'


class TlgUser(models.Model):
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    persian_name = models.CharField(max_length=50)
    real_name = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    tlg_id = models.IntegerField()
    cache = models.TextField(default='')
    cache1 = models.TextField(default='')
    num_seen = models.IntegerField(default=0)
    num_import = models.IntegerField(default=0)
    num_edit = models.IntegerField(default=0)

    def __str__(self):
        return self.real_name + '(@' + self.username + ')'


class File(models.Model):
    page = models.TextField()
    text = models.TextField()
    user = models.ForeignKey(TlgUser, related_name='files', on_delete=models.CASCADE)


class NameId(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    name = models.TextField()
