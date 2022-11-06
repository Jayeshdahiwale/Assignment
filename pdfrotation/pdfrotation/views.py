from django.shortcuts import redirect, render
from django.core.files.storage import FileSystemStorage
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from django.contrib import messages
import mimetypes
import pikepdf
import re
import os
def upload(request):
    final_file = None
    if request.method=='POST':
        try:
            if float(request.POST['angle'])%90 == 0:
                angle = int(request.POST['angle'])
            else:
                messages.info(request,'Please enter the angle multiple of 90')
                return redirect('upload')
            if int(request.POST['pageNumber']):
                page_number = int(request.POST['pageNumber'])
        except ValueError:
            messages.info(request,'Please enter the integer value in page number field.')
            return redirect('upload')
        uploaded_file = request.FILES['document']
        match = re.search('\.pdf$',uploaded_file.name)
        if not match:
            messages.info(request,'Only pdf files are allowed.')
            return redirect('upload')

        fs = FileSystemStorage()
        fs.save(uploaded_file.name,uploaded_file)
        final_file = rotate_file(uploaded_file.name,angle,page_number)
    return render(request,'upload_page.html',context={'final_file':final_file})

def download(request,name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = name
    filepath = base_dir + '\\rotated' +'\\' + filename
    filename = os.path.basename(filepath)
    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(filepath,'rb'),chunk_size),
    content_type = mimetypes.guess_type(filepath[0]))
    response['Content-Length'] = os.path.getsize(filepath)
    response['Content-Disposition'] = 'Attachment;filename=%s' % filename
    return response

def rotate_file(name,angle,page_number):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = base_dir + '/media/' + name
    pdf = pikepdf.Pdf.open(filepath)
    pages = pdf.pages
    if page_number <= len(pages):
        pages[page_number-1].Rotate = angle
    rotatedpath = base_dir + '\\rotated'+ '\\rotated'+ os.path.splitext(name)[0] + '.pdf'
    pdf.save(rotatedpath)
    
    return 'rotated'+ os.path.splitext(name)[0] + '.pdf'

