from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from apppermission.functions import user_is_manager


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(null=True, blank=True, upload_to='appaccounts/images/profiles/', verbose_name='Аватар')
    description = models.TextField(max_length=1000, null=True, blank=True, verbose_name='О себе')
    created = models.DateTimeField(auto_now_add=True, null=True)
    score = models.IntegerField(null=True, blank=True, verbose_name='Баллы')
    index_avatar = models.SmallIntegerField(null=True, blank=True, verbose_name='Индекс аватара')
    need_password = models.BooleanField(null=True, default=False, verbose_name='Нужен пароль')
    
    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('appaccounts:profile_edit')

    def get_name(self):
        if self.user.first_name:
            return self.user.first_name
        else:
            return self.user.username        
            
    def get_avatar_url(self):
        if self.index_avatar and 0 < self.index_avatar <= 12:
            return settings.STATIC_URL + f'images/ico/people/student_avatars/student_avatar{self.index_avatar}.svg'
        if self.avatar:
            return self.avatar.url
        else:
            # return settings.STATIC_URL + 'images/ico/people/user_black.svg'
            return settings.STATIC_URL + 'images/ico/people/student1.svg'

    def get_avatar_white_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return settings.STATIC_URL + 'images/ico/people/student_white.svg'
        
    def get_description(self):
        if self.description:
            return self.description
        else:
            return 'Пользователь пока ничего не написал о себе'

    def get_profile_data(self, fields=None):
        
        profile_data_all = {
            'profile_id': self.id,
            'profile_name': self.user.username,
            'profile_description': self.description,
            'profile_avatar': self.avatar.url if self.avatar else '',
            'profile_url': self.get_absolute_url(),
        }

        if fields:
            profile_data = {}
            for field in fields:
                profile_data[field] = profile_data_all[field]
            return profile_data
        else:
            return profile_data_all

    def get_user_skills_data(self, user=None):
        
        from apptasks.models import Task, Skill
        from apporders.models import Order

        import json

        request_user = self.user if not user else user

        # формируем список оценок только по тем скилам, по которым у юзера есть решенные задачи
        user_order_list = Order.objects.select_related('task__skill').filter(user=request_user)
        user_skills = []
        for user_order in user_order_list:
            
            order_rate = round(user_order.get_rate()['rate'], 1)
            
            try:
                skill = next(item for item in user_skills if item["skill"] == user_order.task.skill)
                skill['rate'] += order_rate
                skill['task_count'] += 1
            except:
                
                order_data = {
                    'skill': user_order.task.skill,
                    'rate': order_rate,
                    'task_count': 1
                }
                user_skills.append(order_data)

            extra_skill_count = user_order.task.get_extra_skill_count()
            if extra_skill_count:
                extra_order_rate = round(order_rate * 30 / 100, 1)
                extra_skill_list = (user_order.task.extra_skill1, user_order.task.extra_skill2, user_order.task.extra_skill3)
                for extra_skill in extra_skill_list:
                    if extra_skill:
                        try:
                            skill = next(item for item in user_skills if item["skill"] == extra_skill)
                            skill['rate'] += extra_order_rate
                            skill['task_count'] += 1
                        except:
                            order_data = {
                                'skill': extra_skill,
                                'rate': extra_order_rate,
                                'task_count': 1
                            }
                            user_skills.append(order_data)
                

        # формируем список всех скилов, которые есть в системе
        # и по каждому добавляем оценку юзера
        skill_list = Skill.objects.all()
        user_skills_data = []
        user_total_rate = 0
        user_total_task_count = 0
        for skill in skill_list:
            skill_data = {
                'skill': str(skill),
                'rate': 0
            }
            try:
                user_skill = next(item for item in user_skills if item["skill"] == skill)
                skill_data['rate'] += user_skill['rate']
                user_total_rate += user_skill['rate']
                user_total_task_count += user_skill['task_count']
            except:
                skill_data['rate'] = 0
                
            user_skills_data.append(skill_data)

        data = {
            'total_task_count': user_total_task_count,
            'total_task_count_display': '--' if user_total_task_count == 0 else str(user_total_task_count),
            'total_rate': round(user_total_rate, 1),
            'total_rate_display': '--' if round(user_total_rate, 1) == 0 else str(round(user_total_rate, 1)),
            'skills_data': user_skills_data
            }

        return data

    @staticmethod
    def get_avatar_list():
        avatar_list = []
        for i in range(12):
            avatar_list.append({'number': i+1, 'url': settings.STATIC_URL + f'images/ico/people/student_avatars/student_avatar{i+1}.svg'})
        return avatar_list

    @property
    def current_lesson(self):
        return self.user.current_lessons.select_related('lesson__module__course').first()
        # if current_lessons.exists():
        #     return current_lessons.select_related('lesson__module__course').first().lesson
        # else:
        #     return None

    @property
    def is_manager(self):
        return user_is_manager(self.user)
