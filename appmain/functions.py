from django.utils.text import slugify


def generate_unique_slug(model, slug, field):

    if slug:
        return slug

    if not field:
        origin_slug_unicode = 'empty'
    else:
        origin_slug_unicode = slugify(field, allow_unicode=True).lower()

    unicode_to_en = {
        'а': 'a',
        'б': 'b',
        'в': 'v',
        'г': 'g',
        'д': 'd',
        'е': 'e',
        'ё': 'e',
        'ж': 'zh',
        'з': 'z',
        'и': 'i',
        'й': 'y',
        'к': 'k',
        'л': 'l',
        'м': 'm',
        'н': 'n',
        'о': 'o',
        'п': 'p',
        'р': 'r',
        'с': 's',
        'т': 't',
        'у': 'u',
        'ф': 'f',
        'х': 'kh',
        'ц': 'c',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'sh',
        'ъ': '',
        'ы': 'y',
        'ь': '',
        'э': 'e',
        'ю': 'yu',
        'я': 'ya',
    }

    origin_slug = ''
    for letter in origin_slug_unicode:
        if letter in unicode_to_en:
            origin_slug += unicode_to_en[letter]
        else:
            origin_slug += letter

    unique_slug = origin_slug
    numb = 1
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = '%s-%d' % (origin_slug, numb)
        numb += 1

    return unique_slug
