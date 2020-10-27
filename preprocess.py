
import re
import argparse
import numpy as np
import pandas as pd

RATING_FILE_NAME = dict({'movie': 'ratings.dat',
                         'book': 'BX-Book-Ratings.csv',
                         'music': 'user_artists.dat',
                         'news': 'ratings.txt'})
SEP = dict({'movie': '::', 'book': ';', 'music': '\t', 'news': '\t'})
THRESHOLD = dict({'movie': 4, 'book': 0, 'music': 0, 'news': 0})


def read_item_index_to_entity_id_file():
    file = '../data/item_index2entity_id.txt'
    print('reading item index to entity id file: ' + file + ' ...')
    i = 0
    for line in open(file, encoding='utf-8').readlines():
        item_index = int(line.strip().split('\t')[0])
        satori_id = int(line.strip().split('\t')[1])
        item_index_old2new[item_index] = i
        entity_id2index[satori_id] = i
        i += 1

def convert_name():
    file = '../data/movies.dat'
    
    print('reading movie name file ...')    
    
    for line in open(file, encoding='latin-1').readlines():
        array = line.strip().split(SEP['movie'])
        item_index = int(array[0])
        item_name = array[1]
        
        item_id2name[item_index]=item_name

    
    print('converting movie name file ...')
    writer = open('../data/'+'movie_name.txt', 'w', encoding='utf-8')
    
    item_cnt = 0
    for item_index, item_name in item_id2name.items():
        writer.write('%d\t%s\n' % (item_index, item_name))
        item_cnt += 1
    writer.close()
    print('number of movies: %d' % item_cnt)
    
    
    
    
def convert_rating():
    #Start processing title
    item_name_pd=pd.read_table('../data/movie_name.txt', header=None,encoding='latin-1', names=['item_id', 'title'])
    #Remove the year in the Title
    pattern = re.compile(r'^(.*)\((\d+)\)$')
    title_map = {val:pattern.match(val).group(1) for ii,val in enumerate(set(item_name_pd['title']))}
    item_name_pd['title'] = item_name_pd['title'].map(title_map)
    #Movie Title to Digital Dictionary
    title_set = set()
    for val in item_name_pd['title'].str.split():
        title_set.update(val)
    
    title_set.add('<PAD>')
    title2int = {val:ii for ii, val in enumerate(title_set)}

    #Convert the movie title into a list of equal length numbers, the length is 15
    title_count = 15
    title_map = {val:[title2int[row] for row in val.split()] for ii,val in enumerate(set(item_name_pd['title']))}
    
    for key in title_map:
        for cnt in range(title_count - len(title_map[key])):
            title_map[key].insert(len(title_map[key]) + cnt,title2int['<PAD>'])
    
    #At this time the title changed to 15 numbers
    item_name_pd['title'] = item_name_pd['title'].map(title_map)
    
    #It stores two columns, one is the old movie index, and the other is the 15 numbers corresponding to the movie name
    item_name_pd.to_csv('../data/movie_new_name.txt', sep='\t', header=None, index=False)
    # ratings_final has four columns, the first column is the user index, the second column is the movie index, the third column is the label (0,1), the fourth column and the following are the list type (15, indicating title information)
    file = '../data/' +RATING_FILE_NAME[DATASET]

    print('reading rating file ...')
    item_set = set(item_index_old2new.values())
    user_pos_ratings = dict()
    user_neg_ratings = dict()

    item_name = dict()      #Stored is the movie name information corresponding to the new item index, a list represented by 15 numbers
    
    for line in open(file, encoding='utf-8').readlines()[1:]:
        array = line.strip().split(SEP[DATASET])

        # remove prefix and suffix quotation marks for BX dataset
        if DATASET == 'book':
            array = list(map(lambda x: x[1:-1], array))

        item_index_old = int(array[1])
        if item_index_old not in item_index_old2new:  # the item is not in the final item set
            continue
        item_index = item_index_old2new[item_index_old]
        
        # CPU operation time is too long
        item_name[item_index]=list(item_name_pd.loc[item_name_pd['item_id']==item_index_old,'title'])
        
        user_index_old = int(array[0])

        rating = float(array[2])
        if rating >= THRESHOLD[DATASET]:
            if user_index_old not in user_pos_ratings:
                user_pos_ratings[user_index_old] = set()
            user_pos_ratings[user_index_old].add(item_index)
        else:
            if user_index_old not in user_neg_ratings:
                user_neg_ratings[user_index_old] = set()
            user_neg_ratings[user_index_old].add(item_index)

    
    print('converting rating file ...')
    writer = open('../data/ratings_final.txt', 'w', encoding='utf-8')
    user_cnt = 0
    user_index_old2new = dict()
    for user_index_old, pos_item_set in user_pos_ratings.items():
        if user_index_old not in user_index_old2new:
            user_index_old2new[user_index_old] = user_cnt
            user_cnt += 1
        user_index = user_index_old2new[user_index_old]
        for item in pos_item_set:
            writer.write('%d\t%d\t1' % (user_index, item))
            for l in item_name[item][0]:
                writer.write('\t%d' % l)
            writer.write('\n')
        unwatched_set = item_set - pos_item_set
        if user_index_old in user_neg_ratings:
            unwatched_set -= user_neg_ratings[user_index_old]
        for item in np.random.choice(list(unwatched_set), size=len(pos_item_set), replace=False):
            writer.write('%d\t%d\t0' % (user_index, item))
            for l in item_name[item][0]:
                writer.write('\t%d' % l)
            writer.write('\n')
        '''
        # It’s not feasible to add a title here, because the CrossCompressUnit unit restricts only two matrix inputs with different shapes, not three.
        for item in pos_item_set:
            writer.write('%d\t%d\t%d\t1\n' % (user_index, integer_encoded[item], item))
        unwatched_set = item_set - pos_item_set
        if user_index_old in user_neg_ratings:
            unwatched_set -= user_neg_ratings[user_index_old]
        for item in np.random.choice(list(unwatched_set), size=len(pos_item_set), replace=False):
            writer.write('%d\t%d\t%d\t0\n' % (user_index, integer_encoded[item] ,item))
        '''
        '''
        # Here you can save the index of the movie name and the movie.
        for item in pos_item_set:
            writer.write('%d\t%s\t%d\t1\n' % (user_index, item_name[item], item))
        unwatched_set = item_set - pos_item_set
        if user_index_old in user_neg_ratings:
            unwatched_set -= user_neg_ratings[user_index_old]
        for item in np.random.choice(list(unwatched_set), size=len(pos_item_set), replace=False):
            writer.write('%d\t%s\t%d\t0\n' % (user_index, item_name[item] ,item))
        '''
    writer.close()
    print('number of users: %d' % user_cnt)
    print('number of items: %d' % len(item_set))


    

def convert_kg():
    print('converting kg.txt file ...')
    entity_cnt = len(entity_id2index)
    relation_cnt = 0

    '''
    item_name_pd=pd.read_csv('../data/movie_new_name.txt', sep='\t', names=['item_id', 'title'])
    
    '''
    item_name = dict()      #Stored is the movie name information corresponding to the new item index, a list represented by 15 numbers
    writer = open('../data/kg_final1.txt', 'w', encoding='utf-8')
    file = open('../data/kg.txt', encoding='utf-8')

    for line in file:
        array = line.strip().split('\t')
        head_old = int(array[0])
        relation_old = array[1]
        tail_old = int(array[2])

        if head_old not in entity_id2index:
            continue
        head = entity_id2index[head_old]
        
        flag=item_name_pd.loc[item_name_pd['item_id']==head_old, 'item_id'].any()
        if flag==True:
            item_name[head]=list(item_name_pd.loc[item_name_pd['item_id']==head_old, 'title'])
        
        
        if tail_old not in entity_id2index:
            entity_id2index[tail_old] = entity_cnt
            entity_cnt += 1
        tail = entity_id2index[tail_old]

        if relation_old not in relation_id2index:
            relation_id2index[relation_old] = relation_cnt
            relation_cnt += 1
        relation = relation_id2index[relation_old]
        
        
        
        writer.write('%d\t%d\t%d' % (head, relation, tail))
        
        if flag==True:
            for l in item_name[head][0]:
                writer.write('\t%d' % l)
            writer.write('\n')
        else:
            for _ in range(15):
                writer.write('\t0')
            writer.write('\n')
        
    writer.close()
    print('number of entities (containing items): %d' % entity_cnt)
    print('number of relations: %d' % relation_cnt)


if __name__ == '__main__':
    np.random.seed(555)

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, default='movie', help='which dataset to preprocess')
    args = parser.parse_args()
    DATASET = args.d

    entity_id2index = dict()
    relation_id2index = dict()
    item_index_old2new = dict()
    item_id2name = dict()

    read_item_index_to_entity_id_file()
    convert_name()
    convert_rating()
    convert_kg()
    

    print('done')

