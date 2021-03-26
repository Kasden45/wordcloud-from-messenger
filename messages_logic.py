# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import json
import random
import copy
from datetime import datetime
from wordcloud import WordCloud, ImageColorGenerator
import numpy as np
import os
import PIL.Image
import fnmatch
from tkinter import *
import re

COLOR = ""
HOURS = 2  # top margin between messages as a response time


def add_dicionaries(first_dic, second_dic):
    """
    Concatenates dictionaries, adding values from the same keys
    """
    for key in second_dic:
        if key in first_dic:
            first_dic[key] += second_dic[key]
        else:
            first_dic[key] = second_dic[key]
    return first_dic


def merge_dictionaries(first_dic, second_dic):
    """
    Concatenates dictionaries with dictionaries, adding values from the same keys recursively
    """
    for dic in first_dic:
        if dic in second_dic:
            for key in second_dic[dic]:
                if key in first_dic[dic]:
                    first_dic[dic][key] += second_dic[dic][key]
                else:
                    first_dic[dic][key] = second_dic[dic][key]
    return first_dic


def curse_words_filter(word):
    """
    Filters out polish curse words
    """
    curse_words = ['chuj', 'chuja', 'chujek', 'chuju', 'chujem', 'chujnia',
                   'chujowy', 'chujowa', 'chujowe', 'cipa', 'cipę', 'cipe', 'cipą',
                   'cipie', 'dojebać', 'dojebac', 'dojebie', 'dojebał', 'dojebal',
                   'dojebała', 'dojebala', 'dojebałem', 'dojebalem', 'dojebałam',
                   'dojebalam', 'dojebię', 'dojebie', 'dopieprzać', 'dopieprzac',
                   'dopierdalać', 'dopierdalac', 'dopierdala', 'dopierdalał',
                   'dopierdalal', 'dopierdalała', 'dopierdalala', 'dopierdoli',
                   'dopierdolił', 'dopierdolil', 'dopierdolę', 'dopierdole', 'dopierdoli',
                   'dopierdalający', 'dopierdalajacy', 'dopierdolić', 'dopierdolic',
                   'dupa', 'dupie', 'dupą', 'dupcia', 'dupeczka', 'dupy', 'dupe', 'huj',
                   'hujek', 'hujnia', 'huja', 'huje', 'hujem', 'huju', 'jebać', 'jebac',
                   'jebał', 'jebal', 'jebie', 'jebią', 'jebia', 'jebak', 'jebaka', 'jebal',
                   'jebał', 'jebany', 'jebane', 'jebanka', 'jebanko', 'jebankiem',
                   'jebanymi', 'jebana', 'jebanym', 'jebanej', 'jebaną', 'jebana',
                   'jebani', 'jebanych', 'jebanymi', 'jebcie', 'jebiący', 'jebiacy',
                   'jebiąca', 'jebiaca', 'jebiącego', 'jebiacego', 'jebiącej', 'jebiacej',
                   'jebia', 'jebią', 'jebie', 'jebię', 'jebliwy', 'jebnąć', 'jebnac',
                   'jebnąc', 'jebnać', 'jebnął', 'jebnal', 'jebną', 'jebna', 'jebnęła',
                   'jebnela', 'jebnie', 'jebnij', 'jebut', 'koorwa', 'kórwa', 'kurestwo',
                   'kurew', 'kurewski', 'kurewska', 'kurewskiej', 'kurewską', 'kurewska',
                   'kurewsko', 'kurewstwo', 'kurwa', 'kurwaa', 'kurwami', 'kurwą', 'kurwe',
                   'kurwę', 'kurwie', 'kurwiska', 'kurwo', 'kurwy', 'kurwach', 'kurwami',
                   'kurewski', 'kurwiarz', 'kurwiący', 'kurwica', 'kurwić', 'kurwic',
                   'kurwidołek', 'kurwik', 'kurwiki', 'kurwiszcze', 'kurwiszon',
                   'kurwiszona', 'kurwiszonem', 'kurwiszony', 'kutas', 'kutasa', 'kutasie',
                   'kutasem', 'kutasy', 'kutasów', 'kutasow', 'kutasach', 'kutasami',
                   'matkojebca', 'matkojebcy', 'matkojebcą', 'matkojebca', 'matkojebcami',
                   'matkojebcach', 'nabarłożyć', 'najebać', 'najebac', 'najebał',
                   'najebal', 'najebała', 'najebala', 'najebane', 'najebany', 'najebaną',
                   'najebana', 'najebie', 'najebią', 'najebia', 'naopierdalać',
                   'naopierdalac', 'naopierdalał', 'naopierdalal', 'naopierdalała',
                   'naopierdalala', 'naopierdalała', 'napierdalać', 'napierdalac',
                   'napierdalający', 'napierdalajacy', 'napierdolić', 'napierdolic',
                   'nawpierdalać', 'nawpierdalac', 'nawpierdalał', 'nawpierdalal',
                   'nawpierdalała', 'nawpierdalala', 'obsrywać', 'obsrywac', 'obsrywający',
                   'obsrywajacy', 'odpieprzać', 'odpieprzac', 'odpieprzy', 'odpieprzył',
                   'odpieprzyl', 'odpieprzyła', 'odpieprzyla', 'odpierdalać',
                   'odpierdalac', 'odpierdol', 'odpierdolił', 'odpierdolil',
                   'odpierdoliła', 'odpierdolila', 'odpierdoli', 'odpierdalający',
                   'odpierdalajacy', 'odpierdalająca', 'odpierdalajaca', 'odpierdolić',
                   'odpierdolic', 'odpierdoli', 'odpierdolił', 'opieprzający',
                   'opierdalać', 'opierdalac', 'opierdala', 'opierdalający',
                   'opierdalajacy', 'opierdol', 'opierdolić', 'opierdolic', 'opierdoli',
                   'opierdolą', 'opierdola', 'piczka', 'pieprznięty', 'pieprzniety',
                   'pieprzony', 'pierdel', 'pierdlu', 'pierdolą', 'pierdola', 'pierdolący',
                   'pierdolacy', 'pierdoląca', 'pierdolaca', 'pierdol', 'pierdole',
                   'pierdolenie', 'pierdoleniem', 'pierdoleniu', 'pierdolę', 'pierdolec',
                   'pierdola', 'pierdolą', 'pierdolić', 'pierdolicie', 'pierdolic',
                   'pierdolił', 'pierdolil', 'pierdoliła', 'pierdolila', 'pierdoli',
                   'pierdolnięty', 'pierdolniety', 'pierdolisz', 'pierdolnąć',
                   'pierdolnac', 'pierdolnął', 'pierdolnal', 'pierdolnęła', 'pierdolnela',
                   'pierdolnie', 'pierdolnięty', 'pierdolnij', 'pierdolnik', 'pierdolona',
                   'pierdolone', 'pierdolony', 'pierdołki', 'pierdzący', 'pierdzieć',
                   'pierdziec', 'pizda', 'pizdą', 'pizde', 'pizdę', 'piździe', 'pizdzie',
                   'pizdnąć', 'pizdnac', 'pizdu', 'podpierdalać', 'podpierdalac',
                   'podpierdala', 'podpierdalający', 'podpierdalajacy', 'podpierdolić',
                   'podpierdolic', 'podpierdoli', 'pojeb', 'pojeba', 'pojebami',
                   'pojebani', 'pojebanego', 'pojebanemu', 'pojebani', 'pojebany',
                   'pojebanych', 'pojebanym', 'pojebanymi', 'pojebem', 'pojebać',
                   'pojebac', 'pojebalo', 'popierdala', 'popierdalac', 'popierdalać',
                   'popierdolić', 'popierdolic', 'popierdoli', 'popierdolonego',
                   'popierdolonemu', 'popierdolonym', 'popierdolone', 'popierdoleni',
                   'popierdolony', 'porozpierdalać', 'porozpierdala', 'porozpierdalac',
                   'poruchac', 'poruchać', 'przejebać', 'przejebane', 'przejebac',
                   'przyjebali', 'przepierdalać', 'przepierdalac', 'przepierdala',
                   'przepierdalający', 'przepierdalajacy', 'przepierdalająca',
                   'przepierdalajaca', 'przepierdolić', 'przepierdolic', 'przyjebać',
                   'przyjebac', 'przyjebie', 'przyjebała', 'przyjebala', 'przyjebał',
                   'przyjebal', 'przypieprzać', 'przypieprzac', 'przypieprzający',
                   'przypieprzajacy', 'przypieprzająca', 'przypieprzajaca',
                   'przypierdalać', 'przypierdalac', 'przypierdala', 'przypierdoli',
                   'przypierdalający', 'przypierdalajacy', 'przypierdolić',
                   'przypierdolic', 'qrwa', 'rozjebać', 'rozjebac', 'rozjebie',
                   'rozjebała', 'rozjebią', 'rozpierdalać', 'rozpierdalac', 'rozpierdala',
                   'rozpierdolić', 'rozpierdolic', 'rozpierdole', 'rozpierdoli',
                   'rozpierducha', 'skurwić', 'skurwiel', 'skurwiela', 'skurwielem',
                   'skurwielu', 'skurwysyn', 'skurwysynów', 'skurwysynow', 'skurwysyna',
                   'skurwysynem', 'skurwysynu', 'skurwysyny', 'skurwysyński',
                   'skurwysynski', 'skurwysyństwo', 'skurwysynstwo', 'spieprzać',
                   'spieprzac', 'spieprza', 'spieprzaj', 'spieprzajcie', 'spieprzają',
                   'spieprzaja', 'spieprzający', 'spieprzajacy', 'spieprzająca',
                   'spieprzajaca', 'spierdalać', 'spierdalac', 'spierdala', 'spierdalał',
                   'spierdalała', 'spierdalal', 'spierdalalcie', 'spierdalala',
                   'spierdalający', 'spierdalajacy', 'spierdolić', 'spierdolic',
                   'spierdoli', 'spierdoliła', 'spierdoliło', 'spierdolą', 'spierdola',
                   'srać', 'srac', 'srający', 'srajacy', 'srając', 'srajac', 'sraj',
                   'sukinsyn', 'sukinsyny', 'sukinsynom', 'sukinsynowi', 'sukinsynów',
                   'sukinsynow', 'śmierdziel', 'udupić', 'ujebać', 'ujebac', 'ujebał',
                   'ujebal', 'ujebana', 'ujebany', 'ujebie', 'ujebała', 'ujebala',
                   'upierdalać', 'upierdalac', 'upierdala', 'upierdoli', 'upierdolić',
                   'upierdolic', 'upierdoli', 'upierdolą', 'upierdola', 'upierdoleni',
                   'wjebać', 'wjebac', 'wjebie', 'wjebią', 'wjebia', 'wjebiemy',
                   'wjebiecie', 'wkurwiać', 'wkurwiac', 'wkurwi', 'wkurwia', 'wkurwiał',
                   'wkurwial', 'wkurwiający', 'wkurwiajacy', 'wkurwiająca', 'wkurwiajaca',
                   'wkurwić', 'wkurwic', 'wkurwi', 'wkurwiacie', 'wkurwiają', 'wkurwiali',
                   'wkurwią', 'wkurwia', 'wkurwimy', 'wkurwicie', 'wkurwiacie', 'wkurwić',
                   'wkurwic', 'wkurwia', 'wpierdalać', 'wpierdalac', 'wpierdalający',
                   'wpierdalajacy', 'wpierdol', 'wpierdolić', 'wpierdolic', 'wpizdu',
                   'wyjebać', 'wyjebac', 'wyjebali', 'wyjebał', 'wyjebac', 'wyjebała',
                   'wyjebały', 'wyjebie', 'wyjebią', 'wyjebia', 'wyjebiesz', 'wyjebie',
                   'wyjebiecie', 'wyjebiemy', 'wypieprzać', 'wypieprzac', 'wypieprza',
                   'wypieprzał', 'wypieprzal', 'wypieprzała', 'wypieprzala', 'wypieprzy',
                   'wypieprzyła', 'wypieprzyla', 'wypieprzył', 'wypieprzyl', 'wypierdal',
                   'wypierdalać', 'wypierdalac', 'wypierdala', 'wypierdalaj',
                   'wypierdalał', 'wypierdalal', 'wypierdalała', 'wypierdalala',
                   'wypierdalać', 'wypierdolić', 'wypierdolic', 'wypierdoli',
                   'wypierdolimy', 'wypierdolicie', 'wypierdolą', 'wypierdola',
                   'wypierdolili', 'wypierdolił', 'wypierdolil', 'wypierdoliła',
                   'wypierdolila', 'zajebać', 'zajebac', 'zajebie', 'zajebią', 'zajebia',
                   'zajebiał', 'zajebial', 'zajebała', 'zajebiala', 'zajebali', 'zajebana',
                   'zajebani', 'zajebane', 'zajebany', 'zajebanych', 'zajebanym',
                   'zajebanymi', 'zajebiste', 'zajebisty', 'zajebistych', 'zajebista',
                   'zajebistym', 'zajebistymi', 'zajebiście', 'zajebiscie', 'zapieprzyć',
                   'zapieprzyc', 'zapieprzy', 'zapieprzył', 'zapieprzyl', 'zapieprzyła',
                   'zapieprzyla', 'zapieprzą', 'zapieprza', 'zapieprzy', 'zapieprzymy',
                   'zapieprzycie', 'zapieprzysz', 'zapierdala', 'zapierdalać',
                   'zapierdalac', 'zapierdalaja', 'zapierdalał', 'zapierdalaj',
                   'zapierdalajcie', 'zapierdalała', 'zapierdalala', 'zapierdalali',
                   'zapierdalający', 'zapierdalajacy', 'zapierdolić', 'zapierdolic',
                   'zapierdoli', 'zapierdolił', 'zapierdolil', 'zapierdoliła',
                   'zapierdolila', 'zapierdolą', 'zapierdola', 'zapierniczać',
                   'zapierniczający', 'zasrać', 'zasranym', 'zasrywać', 'zasrywający',
                   'zesrywać', 'zesrywający', 'zjebać', 'zjebac', 'zjebał', 'zjebal',
                   'zjebała', 'zjebala', 'zjebana', 'zjebią', 'zjebali', 'zjeby']
    return word in curse_words


def flatten_dictionaries(dictionary):
    """
        Flattens dictionaries with dictionaries
    """
    merged_dic = {}
    for dic in dictionary:
        for key in dictionary[dic]:
            if key in merged_dic:
                merged_dic[key] += dictionary[dic][key]
            else:
                merged_dic[key] = dictionary[dic][key]
    return merged_dic


def count_file_one_person(file_arg, one_name, min_length):
    """
    Counts numbers of words longer than *min_length* typed by *one_name* in *file_arg*

    :param file_arg: message file's path
    :param one_name: analysed participant's name
    :param min_length: minimal length for word to be counted
    :return:
    """
    participants_dict = {}
    with open(file_arg, 'r', encoding="utf8") as file:
        file_data = file.read()
        data = json.loads(file_data)
    for name in data["participants"]:  # For every participant
        if name["name"].encode('raw_unicode_escape').decode('utf8') == one_name:
            participants_dict[name["name"].encode('raw_unicode_escape').decode('utf8')] = {}

    for message in data["messages"]:
        if message["sender_name"].encode('raw_unicode_escape').decode('utf8') in participants_dict:
            sender = message["sender_name"].encode('raw_unicode_escape').decode('utf8')
            if "content" in message:  # If it's an actual message
                for word in re.split('; |, |\*|\n| |\u00e2\u0080\u009d|\u00e2\u0080\u009e|:\)|\)', message["content"]):
                    word = word.encode('raw_unicode_escape').decode('utf8')
                    if not curse_words_filter(word.lower()):  # If not a curse word :/
                        if word.lower() not in participants_dict[sender] and len(
                                word) > min_length and sender == one_name:
                            participants_dict[sender][word.lower()] = 1

    return participants_dict


def count_file(file_arg, min_length):
    """
        Counts numbers of words longer than *min_length* typed by every participant in *file_arg*

        :param file_arg: message file's path
        :param min_length: minimal length for word to be counted
        :return:
    """
    participants_dict = {}  # All participants
    msg_by_month_file = {}  # Messages by month
    response_times = {}
    last_messages_time = {}
    messages_count = {}
    total_messages_length = {}
    reactions = {}
    all_messages = {}
    count_response = True
    with open(file_arg, 'r', encoding="utf8") as file:
        filedata = file.read()
        data = json.loads(filedata)  # load json data from file

    for name in data["participants"]:
        encoded_name = name["name"].encode('raw_unicode_escape').decode('utf8')
        participants_dict[encoded_name] = {}
        msg_by_month_file[encoded_name] = {}
        last_messages_time[encoded_name] = 0
        response_times[encoded_name] = {}
        messages_count[encoded_name] = 0
        total_messages_length[encoded_name] = 0
        reactions[encoded_name] = {}
        all_messages[encoded_name] = []

    if len(participants_dict) != 2:
        count_response = False

    for message in data["messages"]:
        if message["sender_name"].encode('raw_unicode_escape').decode('utf8') in participants_dict:
            sender = message["sender_name"].encode('raw_unicode_escape').decode('utf8')

            # ------------------ COUNT RESPONSE TIME ------------------
            if count_response:
                for key in participants_dict.keys():
                    if key != sender:
                        receiver = key
                time = message["timestamp_ms"] // 1000

            msg_date = msg_to_date(message)

            #  Check if tht's a response
            for someone in msg_by_month_file:
                if msg_date not in msg_by_month_file[someone]:
                    msg_by_month_file[someone][msg_date] = 0
                    if count_response:
                        response_times[someone][msg_date] = []

            msg_by_month_file[sender][msg_date] += 1
            if count_response:
                if last_messages_time[sender] == max(
                        last_messages_time.values()) and 0 not in last_messages_time.values():
                    if last_messages_time[receiver] - time < 60 * 60 * HOURS:
                        response_times[receiver][msg_date].append(last_messages_time[receiver] - time)
                last_messages_time[sender] = time
            # ---------------- FINISH COUNTING RESPONSE TIME ------------------
            if "reactions" in message:
                for reaction in message["reactions"]:
                    reaction_emoji = reaction["reaction"]

                    actor = reaction["actor"].encode('raw_unicode_escape').decode('utf8')
                    if actor in reactions:
                        if reaction_emoji in reactions[actor]:
                            reactions[actor][reaction_emoji] += 1
                        else:
                            reactions[actor][reaction_emoji] = 1

            if "content" in message:
                all_messages[sender].append(message["content"])
                messages_count[sender] += 1
                total_messages_length[sender] += len(message["content"])

                for word in re.split('; |, |\*|\n| |\u00e2\u0080\u009d|\u00e2\u0080\u009e|:\)|\)', message["content"]):
                    word = word.encode('raw_unicode_escape').decode('utf8')
                    if not curse_words_filter(word.lower()) and len(word) >= min_length:
                        if word.lower() not in participants_dict[sender]:
                            participants_dict[sender][word.lower()] = 1
                        else:
                            participants_dict[sender][word.lower()] += 1
    return participants_dict, msg_by_month_file, response_times, messages_count, total_messages_length, reactions, all_messages


def color_to_hsl(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
    """
    Generates HSL color format string from *COLOR* name

    :param COLOR
    :return: hsl string with generated color
    """
    global COLOR
    color = COLOR.lower()
    color_dict = {"red": 0,
                  "orange": 30,
                  "yellow": 60,
                  "green": 120,
                  "cyan": 180,
                  "blue": 240,
                  "magenta": 300}

    hue = float(color_dict[color])
    saturation = int(100.0 * 255.0 / 255.0)
    lightness = int(100.0 * float(random.randint(60, 120)) / 255.0)

    return "hsl({}, {}%, {}%)".format(hue, saturation, lightness)


def word_cloud(frequencies, title, mask_img, font, given_color):
    """

    :param frequencies: dictionary with words and their frequencies
    :param title: plot's title
    :param mask_img: mask used as a background of wordcloud
    :param font: wordcloud text font
    :param given_color: wordcloud's color
    :return: generated wordcloud
    """
    global COLOR
    COLOR = given_color
    fig = plt.figure(num="%s' WordCloud" % (title))
    mask = np.array(PIL.Image.open(mask_img))
    image_colors = ImageColorGenerator(mask, default_color=(0, 0, 0))
    wordcloud = WordCloud(font_path=font,
                          relative_scaling=1.0, mask=mask, background_color="white").generate_from_frequencies(
        frequencies)
    plt.title(title)
    plt.rcParams.update({"text.color": "black"})
    plt.rcParams['image.cmap'] = 'gray'

    if COLOR == "Random":
        plt.imshow(wordcloud, interpolation='bilinear')
    elif COLOR == "From mask":
        plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation='bilinear')
    else:
        plt.imshow(wordcloud.recolor(color_func=color_to_hsl), interpolation='bilinear')
    plt.axis("off")
    plt.savefig("Clouds/%s.png" % title, format="png")  # Save in 'Clouds' directory
    plt.draw()
    plt.waitforbuttonpress(0)
    return wordcloud


def create_messenger_statistics(inbox_path):
    """
        Generate all statistics for every conversation in inbox_path

        :param inbox_path: path of inbox directory, containing all conversation directories
        :return: dictionary containing all details for all conversations
    """
    stats_by_conv = {}

    msg_by_month = {}
    msg_count = {}
    msg_length = {}
    response_times_by_months = {}
    all_reactions = {}
    all_messages = {}
    try:
        for _, dirs, _ in os.walk(inbox_path):
            for dir in dirs:  # For every directory (conversation) in inbox_path directory
                for _, _, filenames in os.walk("%s/%s" % (inbox_path, dir)):
                    for filename in filenames:  # For every file in conversation directory
                        if fnmatch.fnmatch(filename, 'message*'):
                            _, new_by_month, new_responses, new_mess_count, new_mess_length, new_reactions, new_messages = \
                                count_file("%s/%s" % ("%s/%s" % (inbox_path, dir), filename), 0)  # Actual counting function

                            if len(msg_by_month) == 0:
                                msg_by_month = new_by_month
                            else:
                                merge_dictionaries(msg_by_month, new_by_month)
                            if len(response_times_by_months) == 0:
                                response_times_by_months = new_responses
                            else:
                                merge_dictionaries(response_times_by_months, new_responses)
                            if len(all_reactions) == 0:
                                all_reactions = new_reactions
                            else:
                                merge_dictionaries(all_reactions, new_reactions)
                            if len(msg_count) == 0:
                                msg_count = new_mess_count
                            else:
                                add_dicionaries(msg_count, new_mess_count)
                            if len(msg_count) == 0:
                                msg_length = new_mess_length
                            else:
                                add_dicionaries(msg_length, new_mess_length)
                            if len(all_messages) == 0:
                                all_messages = new_messages
                            else:
                                for part, msges in new_messages.items():
                                    if part in all_messages:
                                        all_messages[part] += msges
                                    else:
                                        all_messages[part] = msges
                    print("Directory:", dir)
                    for participant, dates in response_times_by_months.items():  # Getting average response time
                        for date in dates:
                            dates[date] = int(sum(dates[date]) / max(1, len(dates[date])))
                    for part in all_reactions:  # Sorting reactions by amounts descending
                        all_reactions[part] = {k: v for k, v in
                                               sorted(all_reactions[part].items(), key=lambda item: item[1],
                                                      reverse=True)}
                    stats_by_conv[dir] = {"response": copy.deepcopy(response_times_by_months),
                                          "msg_count": copy.deepcopy(msg_count),
                                          "msg_by_month": copy.deepcopy(msg_by_month),
                                          "msg_length": copy.deepcopy(msg_length),
                                          "reactions": copy.deepcopy(all_reactions),
                                          "messages": copy.deepcopy(all_messages)}  # Packing conversations details

                    response_times_by_months.clear()
                    all_reactions.clear()
                    msg_count.clear()
                    msg_by_month.clear()
                    msg_length.clear()
                    all_messages.clear()
    except FileNotFoundError as e:
        print(e, "Wrong path")
        return None

    return {k: v for k, v in
            sorted(stats_by_conv.items(), key=lambda conv: sum(conv[1]["msg_count"].values()), reverse=True)}


def create_single_conversation_wordcloud(separated, combined, single_conv_path, image, min_length, font, color):
    """
        Generate wordcloud from one conversation

        :param color: color name
        :param font: font path
        :param min_length: minimum word's length to be counted
        :param image: path to mask image
        :param single_conv_path: path of conversation directory, containing all messages
        :param combined: if 1, wordcloud made of all words in conversation is generated
        :param separated: if 1 every participant will have it's own wordcloud generated
        :return: dictionary containing all details for all conversations
    """
    dictionaries = {}
    try:
        for _, _, filenames in os.walk(single_conv_path):
            for filename in filenames:
                if fnmatch.fnmatch(filename, 'message*'):
                    new_dic, _, _, _, _, _, _ = count_file(
                        "%s/%s" % (single_conv_path, filename), min_length)
                    if len(dictionaries) == 0:
                        dictionaries = new_dic
                    else:
                        merge_dictionaries(dictionaries, new_dic)
    except FileNotFoundError as e:
        print(e, "Wrong directory")
        return None

    if dictionaries == {}:
        print("No data - single conversation")
        return None
    # Sorting words in dictionaries by amounts, creating plots
    if separated == 1:
        for key in dictionaries:
            word_cloud(dictionaries[key], key, image, font, color)
            dic_sorted = {k: v for k, v in sorted(dictionaries[key].items(), key=lambda item: item[1], reverse=True)}
            most_freq(dic_sorted, key, min_length)
    # Sorting words in dictionaries by amounts, creating plots
    if combined == 1:
        all_dic = flatten_dictionaries(dictionaries)
        word_cloud(all_dic, "All participants", image, font, color)
        all_dic_sorted = {k: v for k, v in sorted(all_dic.items(), key=lambda item: item[1], reverse=True)}
        most_freq(all_dic_sorted, "ALL PARTICIPANTS", min_length)


def create_single_participant_wordcloud(single_person_path, name, image, min_length, font, color):
    """
        Generate wordcloud from all words used by 'name' in all conversations in 'inbox' path

        :param name: participant's name
        :param color: color name
        :param font: font path
        :param min_length: minimum word's length to be counted
        :param image: path to mask image
        :param single_person_path: path of inbox directory, containing all conversation directories
        :return: dictionary containing all details for all conversations
    """
    dictionaries = {}
    try:
        for _, dirs, _ in os.walk(single_person_path):
            for dir in dirs:
                for _, dirs2, filenames in os.walk("%s/%s" % (single_person_path, dir)):
                    for filename in filenames:
                        if fnmatch.fnmatch(filename, 'message*'):
                            newDic = count_file_one_person("%s/%s/%s" % (single_person_path, dir, filename), name,
                                                           min_length)  # Counting function
                            print("%s/%s/%s" % (single_person_path, dir, filename))
                            if len(dictionaries) == 0:
                                dictionaries = newDic
                            else:
                                merge_dictionaries(dictionaries, newDic)
    except FileNotFoundError as e:
        print(e, "Wrong directory")
        return None
    if dictionaries == {}:
        print("No data - single person")
        return None
    for key in dictionaries:  # Sorting words in dictionaries by amounts
        word_cloud(dictionaries[key], key, image, font, color)
        dic = {k: v for k, v in sorted(dictionaries[key].items(), key=lambda item: item[1], reverse=True)}
        most_freq(dic, key, min_length)


def most_freq(dictionary, name, min_length):
    """
    Generates plot with *name*'s 20 most used words longer than *min_length*

    :param dictionary:
    :param name:
    :param min_length:
    :return:
    """
    data = []
    for key in dictionary:
        data.append([key, dictionary[key]])
    number_of_words = 0
    for key in dictionary:
        number_of_words += dictionary[key]
    columns = ('word', 'occurrences')
    i = 0
    cell_text = []
    for row in range(20):  # Appending top 20 words
        i += 1
        try:
            cell_text.append(data[row])
            if i > 20:
                break
        except:
            cell_text.append(["", ""])

    row_labels = list(range(1, 21))
    fig, ax = plt.subplots()

    ax.xaxis.set_visible(False)  # Hiding x axis
    ax.yaxis.set_visible(False)  # Hiding y axis
    the_table = ax.table(cellText=cell_text,
                         colWidths=[0.2] * 3,
                         colLabels=columns,
                         rowLabels=row_labels,
                         loc='center')  # Creating table with data
    the_table.auto_set_font_size(False)

    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
    for pos in ['right', 'top', 'bottom', 'left']:
        plt.gca().spines[pos].set_visible(False)

    plt.title("TOP 20 MOST FREQUENTLY USED WORDS by %s\nTotal number of words longer than %s characters: %s" % (
        name, min_length - 1, str(number_of_words)))  # Setting title
    plt.draw()  # Show plot
    plt.waitforbuttonpress(0)


def msg_to_date(message):
    """message format
    {
      "sender_name": "NAme,
      "timestamp_ms": 1590092065273,
      "content": "Ok",
      "type": "Generic"
    }
    """
    date = datetime.fromtimestamp(message["timestamp_ms"] // 1000)
    full_date = date.strftime("%Y"), date.strftime("%m")
    return full_date  # Returns tuple MM,YYYY


def create_graph(dates_dictionaries, title_name, yaxis_name):
    """

    :param dates_dictionaries: dictionary of dictionaries containing dates with amounts of messages
    :param title_name: graph title
    :param yaxis_name: y axis name
    """
    def dic_to_matrix(dic):
        matrix = []
        for date in dic:
            matrix.append((date[1], date[0], dic[date]))
        return matrix

    def sort_matrix_date(matrix):
        while True:
            swaps = 0
            for i in range(0, len(matrix) - 1):
                if matrix[i][1] > matrix[i + 1][1] or matrix[i][1] == matrix[i + 1][1] and matrix[i][0] > matrix[i + 1][
                    0]:
                    matrix[i], matrix[i + 1] = matrix[i + 1], matrix[i]
                    swaps += 1
            if swaps == 0:
                break
        return matrix

    dictionaries = {}
    for person in dates_dictionaries:
        dictionaries[person] = sort_matrix_date(dic_to_matrix(dates_dictionaries[person]))

    months = []
    all_messages = {}
    people = []
    for person in dictionaries:
        for num_tuple in dictionaries[person]:
            months.append("%s/%s" % (num_tuple[0], num_tuple[1][-2:]))
        break
    if len(months) == 0:
        return
    for person in dictionaries:
        people.append(person)
        all_messages[person] = []
        for number in dictionaries[person]:
            all_messages[person].append(number[2])

    """ x = np.arange(len(months))
    width = 0.35"""
    X = np.arange(len(months))
    fig, ax = plt.subplots()

    colors = ['b', 'g', 'r', 'y', 'purple', 'black']
    xs = [0.00]
    for i in range(0, len(people)):
        xs.append((i + 1) / (len(people) + 1))
    # xs=[0.00,0.10,0.20,0.30,0.40,0.50]
    i = 0
    rects_array = []
    for person in all_messages:
        rects_array.append(ax.bar(X + 0.1 + xs[i], all_messages[person], width=xs[1], label=people[i]))
        i += 1

    ax.set_ylabel(yaxis_name)
    ax.set_xlabel('Months')
    ax.set_title(title_name)
    ax.set_xticks(X + xs[len(people) // 2])
    ax.set_xticklabels(months, rotation=270)  # rotated months labels
    ax.legend()

    def autolabel(rects):
        # Showing labels
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', annotation_clip=True)

    plt.show()
