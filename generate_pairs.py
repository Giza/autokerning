cyrillic_upper = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
cyrillic_lower = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
latin_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
latin_lower = "abcdefghijklmnopqrstuvwxyz"
numbers = "0123456789"
punctuation = ".,:;!?-()[]{}'\"/\\"

# List of critical standard Cyrillic kerning pairs (based on common font design practices)
cyrillic_critical = [
    "УА", "УД", "УЖ", "УЗ", "УЛ", "УО", "УС", "УТ", "УЧ", "УЦ", "УЯ", "Уа", "Уд", "Уе", "Уз", "Уо", "Ус", "Ут", "Уц", "Уч", "Уя",
    "ТА", "ТГ", "ТО", "ТС", "ТЬ", "ТЯ", "Та", "Тв", "Тг", "Те", "То", "Тс", "Ть", "Тя", "Ту", "Тц", "Тч", "Тш", "Тщ", "Тъ", "Ты", "Тэ", "Тю",
    "ЧА", "ЧО", "ЧУ", "Ча", "Чо", "Чер", "Чу", "Че",
    "РА", "РГ", "РО", "РУ", "РЯ", "Ра", "Рг", "Ре", "Ро", "РУ", "Ру", "Рс", "Ря",
    "ГА", "ГО", "ГУ", "ГЯ", "Га", "Ге", "Го", "Гр", "Гу", "Гя",
    "АТ", "АУ", "АЧ", "АВ", "АД", "АЖ", "АЗ", "АИ", "АЙ", "АК", "АЛ", "АМ", "АН", "АО", "АП", "АР", "АС", "АФ", "АХ", "АЦ", "АШ", "АЩ", "АЪ", "АЫ", "АЬ", "АЭ", "АЮ", "АЯ",
    "ОТ", "ОУ", "ОЧ",
    "СТ", "СУ", "СЧ",
    "УУ",
    "ВА", "ВО", "ВУ", "Ва", "Во", "Ву", "Вя",
    "ПА", "ПО", "ПУ", "Па", "По", "Пу", "Пя",
    "КА", "КО", "КУ", "КЕ", "Ка", "Ко", "Ку", "Ке",
    "ФА", "ФО", "ФУ", "Фа", "Фо", "Фу", 
    "ЯА", "ЯО", "ЯУ", "Яа", "Яо", "Яу", "Яя",
    "ЬА", "ЬО", "ЬУ", "Ьа", "Ьо", "Ьу", "Ья",
    "ЪА", "ЪО", "ЪУ", "Ъа", "Ъо", "Ъу", "Ъя",
]

# We should generate a reasonable comprehensive list
# Since autokerning will test all generated pairs, we can provide a large list.
all_pairs = []

# Cyrillic-Cyrillic (Upper-Lower and Upper-Upper are most important)
for c1 in cyrillic_upper:
    for c2 in cyrillic_lower:
        all_pairs.append(c1 + c2)
    for c2 in cyrillic_upper:
        all_pairs.append(c1 + c2)

# All Lower-Lower (to handle cases like 'ив' properly)
for c1 in cyrillic_lower:
    for c2 in cyrillic_lower:
        all_pairs.append(c1 + c2)

# All Lower-Upper (to handle cases like 'вЕ')
for c1 in cyrillic_lower:
    for c2 in cyrillic_upper:
        all_pairs.append(c1 + c2)

# Numbers with Numbers
for n1 in numbers:
    for n2 in numbers:
        all_pairs.append(n1 + n2)

# Numbers with Cyrillic (Upper and Lower)
for n in numbers:
    for c in cyrillic_upper + cyrillic_lower:
        all_pairs.append(n + c)
        all_pairs.append(c + n)

# Punctuation with Cyrillic/Numbers
for p in punctuation:
    for c in cyrillic_upper + cyrillic_lower + numbers:
        all_pairs.append(p + c)
        all_pairs.append(c + p)

# Latin-Cyrillic Mixed (Sometimes happens in abbreviations or tech text)
# A-А, T-Т, etc.
for l in latin_upper + latin_lower:
    for c in cyrillic_upper + cyrillic_lower:
        all_pairs.append(l + c)
        all_pairs.append(c + l)

# Remove duplicates
unique_pairs = list(set(all_pairs))

# Formatting for CLI (comma separated string)
with open("cyrillic_pairs.txt", "w", encoding="utf-8") as f:
    f.write(",".join(unique_pairs))
    
print(f"Generated {len(unique_pairs)} pairs to cyrillic_pairs.txt")
