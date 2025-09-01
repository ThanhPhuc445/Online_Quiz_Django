# quiz/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Question, Answer, Subject

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