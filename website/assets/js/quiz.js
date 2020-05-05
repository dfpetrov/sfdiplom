let CHECKED = false
let API = false
let timeStart = Date.now()
let questionHtml = ''
let startCountdown = true
let timeLeft = 0
let checkUrl = ''

function submitAnswer(variants) {
    let elementForm = document.getElementById('form')
    if (elementForm) {

        CHECKED = true
        let formData = new FormData(document.forms.form)
        let xhr = new XMLHttpRequest()

        let nextQuestion = document.getElementById('id_question_id')
        if (nextQuestion) {
            formData.append('next_question', nextQuestion.value)
        }

        let resetUrl = document.getElementById('resetUrl')
        if (resetUrl) {
            formData.append('reset_url', resetUrl.value)
        }

        let exitUrl = document.getElementById('exitUrl')
        if (exitUrl) {
            formData.append('exit_url', exitUrl.value)
        }

        let userAnswers = []
        for (let i = 0; i < variants.length; i++) {
            let answerItem = {
                title: '',
                checked: false
            }
            let label = document.getElementById(variants[i].id + 'Label')
            if (label) {
                answerItem.title = label.innerText
                answerItem.checked = variants[i].checked
            } else {
                if (variants[i].type == 'text') {
                    answerItem.title = variants[i].value
                    if (answerItem.title.trim() != '') {
                        answerItem.checked = true
                    }
                }
            }
            userAnswers.push(answerItem)
        }

        formData.append('user_answers', JSON.stringify(userAnswers))
        formData.append('time_spent', JSON.stringify((Date.now() - timeStart) / 1000))
        formData.append('time_left', JSON.stringify(timeLeft))
        formData.append('show_correct', '1')
        xhr.open('post', checkUrl)
        xhr.send(formData)
        xhr.onload = function () {
            if (xhr.status === 200) {
                let response = JSON.parse(xhr.response)
                let questionContent = document.getElementById('questionContent')
                if (questionContent) {
                    questionContent.innerHTML = response.html_current_question_result
                    hlBlocks()
                }
                questionHtml = response.html_next_question
                ready()
            } else {

            }
        }
        xhr.onerror = function () {

        }

    }
}

function checkAnswer() {
    let variants = document.getElementsByName('user-answer')
    if (variants) {
        startCountdown = false
        let userAnswers = []
        for (let i = 0; i < variants.length; i++) {
            if (variants[i].checked) {
                let label = document.getElementById(variants[i].id + 'Label')
                if (label) {
                    userAnswers.push(label.innerText)
                }
            } else {
                if (variants[i].type == 'text') {
                    userAnswers.push(variants[i].value)
                }
            }
        }
        if (CHECKED === false) {
            if (userAnswers.length > 0 || API === true) {
                submitAnswer(variants)
            } else {
                if (API === false) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Oops...',
                        text: 'Не выбрано ни одного варианта!',
                    })
                }
            }
        }
    }
}

function countdown(seconds) {
    function tick() {
        if (CHECKED === false && startCountdown) {
            updateCountdownText(seconds)
            seconds--
            timeLeft = seconds
            if (seconds >= 0) {
                setTimeout(tick, 1000)
            } else {
                if (CHECKED === false) {
                    API = true
                    checkAnswer()
                }
            }
        }
    }

    tick()
}

function updateCountdownText(seconds) {
    let counter = document.getElementById("countdown")
    if (counter) {
        let minutes = 0
        if (seconds >= 60) {
            minutes = (seconds - seconds % 60) / 60
        }
        let current_seconds = seconds - minutes * 60
        counter.innerHTML = minutes.toString() + ":" + (current_seconds < 10 ? "0" : "") + String(current_seconds)
        if (seconds <= 13) {
            counter.classList.remove('text-black-50')
            counter.classList.add('text-warning')
        }
        if (seconds <= 4) {
            counter.classList.remove('text-warning')
            counter.classList.add('text-accent')
        }
    }
}

function ready() {

    let btnCheck = document.getElementById('btnCheck')
    if (btnCheck) {
        btnCheck.onclick = function () {
            checkAnswer()
        }
    }

    let btnNext = document.getElementById('btnNext')
    if (btnNext) {
        btnNext.onclick = function () {
            let questionContent = document.getElementById('questionContent')
            if (questionContent) {
                questionContent.innerHTML = questionHtml
                startCountdown = true
                let questionNumber = document.getElementById('questionNumber')
                let questionCount = document.getElementById('questionCount')
                let questionNumberText = document.getElementById('questionNumberText')
                if (questionNumber && questionCount && questionNumberText) {
                    questionNumberText.innerText = 'Вопрос ' + questionNumber.value + ' из ' + questionCount.value
                }
                ready()
            }
        }
    }

    let btnRestart = document.getElementById('btnRestart')
    if (btnRestart) {
        btnRestart.onclick = function () {
            let restartUrl = document.getElementById('restartUrl')
            let elementForm = document.getElementById('formReset')
            if (restartUrl && elementForm) {
                let xhr = new XMLHttpRequest()
                let formData = new FormData(document.forms.formReset)
                xhr.open('post', restartUrl.value)
                xhr.send(formData)
                xhr.onload = function () {
                    if (xhr.status === 200) {
                        let response = JSON.parse(xhr.response)
                        if (response) {
                            window.location = response.next
                        }
                    } else {
                        alert('Кажется сервер упал :( Мы уже работаем над этим. Пока отдохни, выпей чайку')
                    }
                }
                xhr.onerror = function () {
                    alert('Кажется сервер упал :( Мы уже работаем над этим. Пока отдохни, выпей чайку')
                }

            }
        }
    }

    let btnExit = document.getElementById('btnExit')
    if (btnExit) {
        btnExit.onclick = function () {
            let xhr = new XMLHttpRequest()
            let formData = new FormData(document.forms.form)
            formData.append('mode_exit', '0')
            xhr.open('post', '{{ check_url }}')
            xhr.send(formData)
            xhr.onload = function () {
                if (xhr.status === 200) {
                    window.location = '{{ next_lesson_url }}'
                } else {
                    alert('Кажется сервер упал :( Мы уже работаем над этим. Пока отдохни, выпей чайку')
                }
            }
            xhr.onerror = function () {
                alert('Кажется сервер упал :( Мы уже работаем над этим. Пока отдохни, выпей чайку')
            }
        }
    }

    CHECKED = false
    API = false
    timeStart = Date.now()

    let quizCompleted = document.getElementById('quizCompleted')
    if (quizCompleted) {
        startCountdown = startCountdown && quizCompleted.value == '0';
    }

    let needCountdown = document.getElementById('needCountdown')
    if (needCountdown && needCountdown.value == '1') {
        let timeElement = document.getElementById('timeLeft')
        if (timeElement) {
            timeLeft = Number(timeElement.value)
        }
        updateCountdownText(timeLeft)
        if (startCountdown) {
            countdown(timeLeft)
        }
    }

    let checkUrlElement = document.getElementById('checkUrl')
    if (checkUrlElement) {
        checkUrl = checkUrlElement.value
    }

    hlBlocks()

}

function hlBlocks() {
    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block)
    })
}

document.addEventListener("DOMContentLoaded", ready)
