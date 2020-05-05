from django import forms
from .models import Course, Module, Lesson, CompletedLesson, Content, CourseEnroll, Quiz, Question


class CourseCreationForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control form-control-lg', 'placeholder': 'Название'})
        self.fields['overview'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Краткое описание', 'rows': '3'})
        self.fields['description'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Полное описание', 'rows': '10'})
        self.fields['profit'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Чему ты научишься после прохождения курса',
             'rows': '10'})
        self.fields['subject'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Раздел'})
        self.fields['language'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Язык программирования'})
        self.fields['level'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Уровень'})
        self.fields['avatar'].widget.attrs.update(
            {'form': 'form'})


class CourseUpdateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control form-control-lg', 'placeholder': 'Название'})
        self.fields['overview'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Краткое описание', 'rows': '3'})
        self.fields['description'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Полное описание', 'rows': '10'})
        self.fields['profit'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Чему ты научишься после прохождения курса',
             'rows': '10'})
        self.fields['subject'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Раздел'})
        self.fields['language'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Язык программирования'})
        self.fields['level'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Уровень'})
        self.fields['slug'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Slug', 'readonly': True})
        self.fields['avatar'].widget.attrs.update(
            {'form': 'form'})


class ModuleUpdateForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'active', 'slug', 'order', 'need_review']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control form-control-lg', 'placeholder': 'Название'})
        self.fields['description'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Полное описание', 'rows': '3'})
        self.fields['slug'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Slug', 'readonly': True})
        self.fields['order'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'order', 'readonly': True})
        self.fields['need_review'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'need_review', 'readonly': True})


class LessonUpdateForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'active', 'slug', 'order', 'type', 'quiz']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control form-control-lg', 'placeholder': 'Название'})
        self.fields['description'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Полное описание', 'rows': '3'})
        self.fields['slug'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Slug', 'readonly': True})
        self.fields['order'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Order', 'readonly': True})
        self.fields['type'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Type'})
        self.fields['quiz'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Quiz', 'readonly': True})

    def clean_quiz(self):
        quiz = self.cleaned_data['quiz']
        if quiz and self.cleaned_data['type'] != Lesson.QUIZ:
            raise forms.ValidationError('У лекции должен быть установлен тип quiz, чтобы можно было привязать тест')
        elif not quiz and self.cleaned_data['type'] == Lesson.QUIZ:
            raise forms.ValidationError('Тест не выбран! Нужно указать тест.')
        elif quiz and self.cleaned_data['type'] == Lesson.QUIZ and quiz.type != Quiz.LESSON:
            raise forms.ValidationError(
                f'У теста должен стоять тип lesson чтобы его можно было привязать к уроку. Сейчас у теста {quiz.title} выбран тип {quiz.get_type_display()}')
        return quiz


class ContentUpdateForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['slug', 'order', 'quiz']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Slug', 'readonly': True})
        self.fields['order'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Slug', 'readonly': True})
        self.fields['quiz'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Slug', 'readonly': True})


class CourseEnrollForm(forms.ModelForm):
    class Meta:
        model = CourseEnroll
        fields = ('course',)
        widgets = {
            'course': forms.HiddenInput(),
        }


class CompleteLessonForm(forms.ModelForm):
    class Meta:
        model = CompletedLesson
        fields = ('lesson',)
        widgets = {
            'lesson': forms.HiddenInput(),
        }


class QuizCreationForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control form-control-lg', 'placeholder': 'Название'})
        self.fields['overview'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Краткое описание'})
        self.fields['description'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Полное описание', 'rows': '3'})
        self.fields['subject'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Раздел'})
        self.fields['level'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Уровень'})
        self.fields['language'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Язык программирования'})
        self.fields['avatar'].widget.attrs.update(
            {'form': 'form'})
        self.fields['type'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Тип теста'})
        self.fields['time_type'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Тип времени'})
        self.fields['duration'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Время'})
        self.fields['index_avatar'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Номер изображения'})

    def clean_duration(self):
        # super(QuizCreationForm, self).clean_duration()
        duration = self.cleaned_data['duration']
        time_type = self.cleaned_data['time_type']
        if time_type == Quiz.TIME_TYPE_QUIZ and not self.cleaned_data['duration']:
            raise forms.ValidationError('Не указано время на тест. Это обязательное поле т.к. тип теста QuizTime')
        return duration


class QuizUpdateForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('subject',
                  'language',
                  'title',
                  'description',
                  'index_avatar',
                  'type', 'avatar', 'slug', 'overview', 'level', 'time_type', 'duration')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].widget.attrs.update({'form': 'form', 'class': 'custom-select form-control'})
        self.fields['language'].widget.attrs.update({'form': 'form', 'class': 'form-control'})
        self.fields['level'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Уровень'})
        self.fields['title'].widget.attrs.update({'form': 'form', 'class': 'form-control', 'placeholder': 'Название'})
        self.fields['overview'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Краткое описание'})
        self.fields['description'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Полное описание', 'rows': '5'})
        self.fields['type'].widget.attrs.update({'form': 'form', 'class': 'custom-select form-control'})
        self.fields['avatar'].widget.attrs.update({'form': 'form'})
        self.fields['slug'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Slug', 'readonly': True})
        self.fields['time_type'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control custom-select', 'placeholder': 'Тип времени'})
        self.fields['duration'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Время в секундах'})
        self.fields['index_avatar'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Номер изображения'})

    def clean(self):
        cleaned_data = super(QuizUpdateForm, self).clean()
        duration = cleaned_data.get('duration')
        quiz_type = cleaned_data.get('type')
        time_type = cleaned_data.get('time_type')

        if time_type == Quiz.TIME_TYPE_QUIZ and not duration:
            msg = 'Не указано время на тест. Это обязательное поле т.к. тип теста QuizTime'
            self._errors['time_type'] = self.error_class([msg])
            del cleaned_data['time_type']

        if time_type == Quiz.TIME_TYPE_QUESTION:
            questions = self.instance.questions.filter(duration=0)
            if questions.exists():
                q_list = ''
                i = 1
                for item in questions:
                    q_list += f'{i}: {item.title}, '
                    i += 1
                msg = f'Не возможно установить тип QuestionTime т.к. не указано время у следующих вопросов: {q_list}'
                self._errors['time_type'] = self.error_class([msg])
                del cleaned_data['time_type']

        if quiz_type != Quiz.LESSON:
            lesson_for_this_quiz = Lesson.objects.filter(quiz=self.instance)
            if lesson_for_this_quiz:
                msg_list = ['У теста нельзя изменить тип т.к. он выбран в следующих уроках:']
                for item in lesson_for_this_quiz:
                    msg_list.append(f' - {item.title}. Курс: {item.module.course}. Модуль {item.module}')
                self._errors['type'] = self.error_class(msg_list)
                del cleaned_data['type']

        return cleaned_data


class QuestionUpdateForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('title', 'text', 'description', 'code', 'type', 'score', 'expected_result', 'duration')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'placeholder': 'Название вопроса'})
        self.fields['text'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control',
             'placeholder': 'Текст вопроса', 'rows': '5'})
        self.fields['description'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'rows': '3',
             'placeholder': 'Примечание (пояснение вопроса или подсказка)'})
        self.fields['code'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'rows': '5',
             'placeholder': 'Код к вопросу'})
        self.fields['expected_result'].widget.attrs.update(
            {'form': 'form', 'class': 'form-control', 'rows': '5',
             'placeholder': 'Ожидаемый результат'})
        self.fields['type'].widget.attrs.update({'form': 'form', 'class': 'custom-select form-control'})
        self.fields['score'].widget.attrs.update({'form': 'form', 'class': 'form-control'})
        self.fields['duration'].widget.attrs.update({'form': 'form', 'class': 'form-control'})

    def clean_duration(self):
        # super(QuestionUpdateForm, self).clean_duration()
        duration = self.cleaned_data['duration']
        if self.instance.quiz.time_type == Quiz.TIME_TYPE_QUESTION and not self.cleaned_data['duration']:
            raise forms.ValidationError('Не указано время на вопрос. Это обязательное поле т.к. тип теста QuestionTime')
        return duration


class QuizProgressForm(forms.Form):
    quiz_id = forms.CharField(widget=forms.HiddenInput)
    question_id = forms.CharField(widget=forms.HiddenInput)
