from count import predict as predict_count
from detect import predict as predict_detect

import numpy as np

threshold_d1 = 20
threshold_d2 = 50
threshold_c1 = 50
threshold_c2 = 90

"""
Count\detection | 0-d1 | d1-d2 | d2-+oo
    0-c1        |  11  |  12   | 13
    c1-c2       |  21  |  22   | 23
    c2-+oo      |  31  |  32   | 33
"""
def predict(img):
    nb_person_counted, density_map = predict_count(img)
    bboxes = predict_detect(img)

    nb_person_detected = len(bboxes)

    case_d =  np.array([0,threshold_d1,threshold_d2]) - nb_person_detected
    case_d = np.where(case_d < 0, case_d, - np.inf).argmax() + 1

    case_c =  np.array([0,threshold_c1,threshold_c2]) - nb_person_counted
    case_c = np.where(case_c < 0, case_c, - np.inf).argmax() + 1

    case_cd = int("%d"%case_c + "%d"%case_d)

    if case_cd == 11:
        nb_person = nb_person_detected
    elif case_cd == 12:
        nb_person = nb_person_detected
    elif case_cd == 13:
        nb_person = nb_person_detected
    elif case_cd == 21:
        nb_person = (nb_person_detected + nb_person_counted) // 2
    elif case_cd == 22:
        nb_person = (nb_person_detected + nb_person_counted) // 2
    elif case_cd == 23:
        nb_person = nb_person_counted
    elif case_cd == 31:
        nb_person = nb_person_counted
    elif case_cd == 32:
        nb_person = nb_person_counted
    elif case_cd == 33:
        nb_person = nb_person_counted
    else:
        raise Exception('Case not supported')
    return nb_person, density_map, bboxes
