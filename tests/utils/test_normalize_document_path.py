from annotatedocs.utils import normalize_document_path


def test_lowercasing():
    assert normalize_document_path('INSTALL') == 'install'
    assert normalize_document_path('Index') == 'index'
    assert normalize_document_path('homePage') == 'homepage'


def test_remove_non_letter_prefix():
    assert normalize_document_path('01tutorial') == 'tutorial'
    assert normalize_document_path('_index') == 'index'
    assert normalize_document_path('___12___index') == 'index'
    assert normalize_document_path('howtos/01_how_to_rock') == 'howtos/how_to_rock'


def test_dashes_to_underscore():
    assert normalize_document_path('license-text') == 'license_text'
    assert normalize_document_path('more-stuff/jokes_about-php') == 'more_stuff/jokes_about_php'


def test_remove_short_bits():
    assert normalize_document_path('m/matching') == 'matching'
    assert normalize_document_path('matching/m') == 'matching'
    assert normalize_document_path('ref/short') == 'ref/short'
    assert normalize_document_path('api/01_A') == 'api'
    assert normalize_document_path('api/01_A/index') == 'api/index'
    assert normalize_document_path('related/1a2b3cd4ef') == 'related'


def test_none_result():
    assert normalize_document_path('to/sh/or/t') is None
    assert normalize_document_path('123_!!a32') is None
