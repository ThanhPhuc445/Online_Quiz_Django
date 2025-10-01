# quiz/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import Question, Answer, Subject, Quiz

# ===========================================================================
# FORMSET CHO CÂU HỎI VÀ ĐÁP ÁN (Question & Answer)
# ===========================================================================

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
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input ms-2'}),
        }
        labels = {
            'text': 'Nội dung đáp án',
            'is_correct': 'Là đáp án đúng?',
        }

AnswerFormSet = inlineformset_factory(
    Question, 
    Answer, 
    form=AnswerForm, 
    extra=4, 
    max_num=4, 
    can_delete=False,
    validate_min=True,
    min_num=1
)


# ===========================================================================
# FORM CHO ĐỀ THI (QUIZ) - ĐÃ ĐƯỢC THIẾT KẾ LẠI
# ===========================================================================

class QuizForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Lấy 'user' được truyền từ view
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Lọc danh sách câu hỏi để giáo viên chỉ thấy câu hỏi của mình
            self.fields['questions'].queryset = Question.objects.filter(created_by=user)

    # Lựa chọn chế độ Công khai / Riêng tư
    PRIVACY_CHOICES = [
        ('True', 'Công khai (Tất cả học sinh đều có thể thấy và tham gia)'),
        ('False', 'Riêng tư (Học sinh cần nhập mã code để được tham gia)'),
    ]
    is_public = forms.ChoiceField(
        choices=PRIVACY_CHOICES,
        widget=forms.RadioSelect,
        label="Chế độ hiển thị",
        initial='True', # Mặc định là 'Công khai'
        help_text="Chọn chế độ hiển thị cho đề thi của bạn."
    )

    # Các trường hiển thị thời gian với widget phù hợp
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Thời gian bắt đầu"
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Thời gian kết thúc"
    )

    class Meta:
        model = Quiz
        # Xóa 'allowed_students', thêm 'is_public'
        fields = ['title', 'subject', 'duration_minutes', 'start_time', 'end_time', 'is_public', 'questions']
        labels = {
            'title': 'Tiêu đề đề thi',
            'subject': 'Môn học',
            'duration_minutes': 'Thời gian làm bài (phút)',
            'questions': 'Chọn câu hỏi từ ngân hàng'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'questions': forms.CheckboxSelectMultiple, # Hiển thị câu hỏi dưới dạng checkbox
        }
        
    def clean_is_public(self):
        # Chuyển đổi giá trị chuỗi ('True'/'False') từ radio button thành boolean
        return self.cleaned_data['is_public'] == 'True'