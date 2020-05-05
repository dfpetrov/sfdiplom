def get_html_from_form_errors(form):
    errors = ''
    if form.errors:
        errors = '<ol>'
        for field in form:
            for error in field.errors:
                errors += f'<li>{field.name} - {error}; </li>'
        errors += '</ol>'
    return errors


def plural_form(value, form1, form2, form5):
    if not value:
        value = 0
    n = abs(value) % 100
    n1 = n % 10
    result_form = form5
    if 10 < n < 20:
        result_form = form5
    elif 1 < n1 < 5:
        result_form = form2
    elif n1 == 1:
        result_form = form1
    return f'{value} {result_form}'
