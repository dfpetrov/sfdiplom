from django.urls import reverse, reverse_lazy


class BreadCrumbType:
    DASHBOARD = 'DASHBOARD'
    DASHBOARD_MANAGE = 'DASHBOARD_MANAGE'
    QUIZZES_MANAGE = 'QUIZZES_MANAGE'
    COURSE_LIBRARY = 'COURSE_LIBRARY'
    EXAMS = 'EXAMS'
    MY_ACHIEVEMENTS = 'MY_ACHIEVEMENTS'


class BreadCrumb:
    title = ''
    url = ''

    def __init__(self, type_bc=None, user=None, **kwargs):
        title = ''
        url = ''
        if 'title' in kwargs:
            title = kwargs['title']
        elif 'object' in kwargs:
            try:
                title = kwargs['object'].title
            except:
                title = str(kwargs['object'])
        if 'url' in kwargs:
            url = kwargs['url']
        elif 'object' in kwargs:
            if 'mode' in kwargs:
                if kwargs['mode'] == 'admin':
                    try:
                        url = kwargs['object'].get_manage_url()
                    except:
                        url = ''
                else:
                    try:
                        url = kwargs['object'].get_absolute_url()
                    except:
                        url = ''
        if not title:
            if type_bc == BreadCrumbType.DASHBOARD:
                title = 'Home'
            elif type_bc == BreadCrumbType.COURSE_LIBRARY:
                title = 'Библиотека курсов'
            elif type_bc == BreadCrumbType.QUIZZES_MANAGE:
                title = 'Тесты'
            elif type_bc == BreadCrumbType.DASHBOARD_MANAGE:
                title = 'Панель управления'
            elif type_bc == BreadCrumbType.EXAMS:
                title = 'Испытания'
            elif type_bc == BreadCrumbType.MY_ACHIEVEMENTS:
                title = 'Мои достижения'
        if not url:
            if type_bc == BreadCrumbType.DASHBOARD:
                if user and user.is_authenticated:
                    url = reverse('appmain:dashboard')
                else:
                    url = reverse('appmain:index')
            elif type_bc == BreadCrumbType.QUIZZES_MANAGE:
                url = reverse('appmain:dashboard_manage_section', kwargs={'section': 'quizzes'})
            elif type_bc == BreadCrumbType.COURSE_LIBRARY:
                url = reverse('appcourses:library')
            elif type_bc == BreadCrumbType.DASHBOARD_MANAGE:
                url = reverse('appmain:dashboard_manage')
            elif type_bc == BreadCrumbType.EXAMS:
                url = reverse('appmain:exams')
            elif type_bc == BreadCrumbType.MY_ACHIEVEMENTS:
                url = reverse('appmain:my_achievements')

        self.title = title
        self.url = url
