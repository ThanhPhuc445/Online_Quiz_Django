# quiz/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import Question, Answer, Subject, Quiz

# ===========================================================================
# FORMSET CHO CÂU HỎI VÀ ĐÁP ÁN (Question & Answer) - ĐÃ CẬP NHẬT
# ===========================================================================

class QuestionForm(forms.ModelForm):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Môn học"
    )
    
    class Meta:
        model = Question
        fields = ['subject', 'text', 'question_type', 'difficulty', 'correct_answer_text']
        labels = {
            'text': 'Nội dung câu hỏi',
            'question_type': 'Loại câu hỏi',
            'difficulty': 'Độ khó',
            'correct_answer_text': 'Đáp án đúng (cho tự luận)'
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'id': 'id_text'}),
            'question_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_question_type'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'correct_answer_text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Nhập đáp án mẫu cho câu tự luận...',
                'id': 'id_correct_answer_text'
            }),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control answer-text'}),
            'is_correct': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'text': 'Nội dung đáp án',
            'is_correct': 'Là đáp án đúng?',
        }

# Custom FormSet để xử lý logic theo loại câu hỏi
class DynamicAnswerFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.question_type == Question.QuestionType.TRUE_FALSE:
            # Tự động tạo đáp án Đúng/Sai nếu chưa có
            if not self.queryset.exists():
                self.initial = [
                    {'text': 'Đúng', 'is_correct': False},
                    {'text': 'Sai', 'is_correct': False}
                ]

    def clean(self):
        super().clean()
        question_type = self.instance.question_type if self.instance else None
        
        if question_type == Question.QuestionType.SINGLE_CHOICE:
            correct_answers = sum(1 for form in self.forms if form.cleaned_data.get('is_correct') and not form.cleaned_data.get('DELETE', False))
            if correct_answers != 1:
                raise forms.ValidationError("Câu hỏi một lựa chọn phải có duy nhất 1 đáp án đúng")
        
        elif question_type == Question.QuestionType.MULTIPLE_CHOICE:
            correct_answers = sum(1 for form in self.forms if form.cleaned_data.get('is_correct') and not form.cleaned_data.get('DELETE', False))
            if correct_answers < 1:
                raise forms.ValidationError("Câu hỏi nhiều lựa chọn phải có ít nhất 1 đáp án đúng")
        
        elif question_type == Question.QuestionType.TRUE_FALSE:
            correct_answers = sum(1 for form in self.forms if form.cleaned_data.get('is_correct') and not form.cleaned_data.get('DELETE', False))
            if correct_answers != 1:
                raise forms.ValidationError("Câu hỏi Đúng/Sai phải có duy nhất 1 đáp án đúng")

AnswerFormSet = inlineformset_factory(
    Question, 
    Answer, 
    form=AnswerForm,
    formset=DynamicAnswerFormSet,
    extra=4, 
    max_num=6, 
    can_delete=True,
    validate_min=True,
    min_num=1
)


# ===========================================================================
# FORM CHO ĐỀ THI (QUIZ) - ĐÃ ĐƯỢC THIẾT KẾ LẠI VÀ THÊM allow_multiple_attempts
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

    # THÊM FIELD CHO PHÉP THI NHIỀU LẦN - QUAN TRỌNG!
    allow_multiple_attempts = forms.BooleanField(
        required=False,
        initial=False,
        label="Cho phép thi nhiều lần",
        help_text="Nếu bật, học sinh có thể làm bài nhiều lần (chế độ luyện tập). Nếu tắt, học sinh chỉ được thi 1 lần duy nhất.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
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
        # THÊM 'allow_multiple_attempts' vào fields
        fields = ['title', 'subject', 'duration_minutes', 'start_time', 'end_time', 'is_public', 'allow_multiple_attempts', 'questions']
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