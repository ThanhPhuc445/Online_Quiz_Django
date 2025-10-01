# quiz/forms.py
from django import forms
from django.forms import inlineformset_factory

from users.models import User
from .models import Question, Answer, Subject, Quiz

class QuizForm(forms.ModelForm):
    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.none(),  # Ban đầu không có câu hỏi nào
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Chọn các câu hỏi cho đề thi"
    )
    allowed_students = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Chọn học sinh được phép làm bài"
    )
    class Meta:
        model = Quiz
        fields = ['title', 'subject', 'duration_minutes', 'start_time', 'end_time', 'questions']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        labels = {
            'title': 'Tiêu đề bài kiểm tra',
            'subject': 'Môn học',
            'duration_minutes': 'Thời lượng (phút)',
            'start_time': 'Thời gian bắt đầu',
            'end_time': 'Thời gian kết thúc',
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(QuizForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['questions'].queryset = Question.objects.filter(created_by=user)
        self.fields['allowed_students'].queryset = User.objects.filter(is_staff=False)
class QuestionForm(forms.ModelForm):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Môn học"
    )

    class Meta:
        model = Question
        fields = ['subject', 'text', 'difficulty']
        labels = {
            'text': 'Nội dung câu hỏi',
            'difficulty': 'Độ khó',
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
        labels = {
            'text': 'Nội dung đáp án',
            'is_correct': 'Là đáp án đúng?',
        }
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Formset để quản lý nhiều Answer cùng lúc cho một Question
AnswerFormSet = inlineformset_factory(
    Question,  # Model cha
    Answer,    # Model con
    form=AnswerForm,
    extra=4,   # Hiển thị 4 form trống
    max_num=4, # Tối đa 4 đáp án
    can_delete=False,
    validate_min=True, # Bắt buộc phải có ít nhất 1 đáp án
)