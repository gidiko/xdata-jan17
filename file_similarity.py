
# coding: utf-8

# In[1]:

import os
import numpy as np


# In[2]:

# cum_size_limit is the cumulative size of input_dir files starting
# from smaller and going to larger-size ones; we pick those, thus "avoiding"
# really large files
def pick_fnames(input_dir, cum_size_limit):
    
    meta_fname_list = os.listdir(input_dir)
    
    # let's get the sizes
    fpath_sizes = []
    for meta_fname in meta_fname_list:
        meta_fpath = os.path.join(input_dir, meta_fname)
        fpath_sizes.append([meta_fpath, os.path.getsize(meta_fpath)])

    # let's pick the ones that fit our cumulative size budget
    sizes = np.array([x[1] for x in fpath_sizes])
    sorting_indices = np.argsort(sizes)

    cum_sizes = np.cumsum(sizes[sorting_indices])
    for i, cum_size in enumerate(cum_sizes):
        if cum_size > cum_size_limit:
            limit_idx = i
            break
            
    # here, picking is actually made
    meta_fname_list = [meta_fname_list[sorting_indices[i]] for i in range(limit_idx)]
    
    return meta_fname_list
    


# In[7]:

# get path -> idx and entry -> idx dictionaries 
# entry can be any info item, e.g. email, SSN
def generate_lookup_tables(input_dir, meta_fname_list):

    # maintain a dictionary to indices as appearing in meta_fname_items
    seqidx_to_realidx = {}
    for seqidx, meta_fname in enumerate(meta_fname_list):
        realidx = int(meta_fname.split('.')[0])
        seqidx_to_realidx[seqidx] = realidx

    # read the files and collect names and entries (e.g. emails) in lists    
    fpath_list = []
    info_list = []

    for meta_fname in meta_fname_list:
        meta_fpath = os.path.join(input_dir, meta_fname)
        with open(meta_fpath, 'r') as f:
            lines = [x.strip() for x in f.readlines()]
            fpath = lines[0]
            size = os.path.getsize(meta_fpath)
            fpath_list.append(fpath)
            try:
                for info in lines[1:]:
                    info_list.append(info)
            except:
                pass

    # towards path -> idx and entry -> idx dictionaries;
    # idx, in path -> idx corresponds to the the ones in input_dir filenames
    # (for reference back to the "sources")
    uniq_fpath_list = fpath_list        
    uniq_info_list = list(set(info_list))
    
    # XXX THE FOLLOWING 2 LINES TAKE THE LION'S SHARE IN COMPUTING TIME!!!
    # THIS IS THE PLACE TO OPTIMIZE!!
    fpath_to_idx = dict([[entry, seqidx_to_realidx[idx]] for idx, entry in enumerate(uniq_fpath_list)])
    info_to_idx = dict([[entry, idx + 1] for idx, entry in enumerate(uniq_info_list)])

    return fpath_to_idx, info_to_idx


# In[8]:

# map to each filepath index the list of indices into the list of info items, e.g. emails;
# from this, pairs of file path indices can be assigned similarities, essentially based on
# the "overlap" of the lists of e.g. email indices each of the path indices in the pair is
# mapped to.
def generate_cross_lookup_table(input_dir, meta_fname_list, fpath_to_idx, info_to_idx):
    
    # second pass over the data files   
    fpathidx_to_infoidxlist = {}
    for meta_fname in meta_fname_list:
        meta_fpath = os.path.join(input_dir, meta_fname)
        with open(meta_fpath, 'r') as f:
            lines = [x.strip() for x in f.readlines()]
            fpath = lines[0]
            fpathidx = fpath_to_idx[fpath]
            infoidxlist = []
            try:
                for info in lines[1:]:
                    infoidxlist.append(info_to_idx[info])
            except:
                pass
            fpathidx_to_infoidxlist[fpathidx] = infoidxlist
    
    return fpathidx_to_infoidxlist


# In[9]:

# write the 3 lookups to disk under output_dir which is assumed to exist;
# for the cross-lookup table the first number in the line is the file path index
# and all the other number in the same line (if any) correspond to indices of the
# entries/attributes/info, e.g. indices of the emails
def write_lookups(output_dir, fpath_to_idx, info_to_idx, fpathidx_to_infoidxlist):
    
    # inverting the dicts for convenience:
    # idx -> path and idx -> entry dicts
    idx_to_fpath = {}
    for entry, idx in fpath_to_idx.iteritems():
        idx_to_fpath[idx] = entry

    idx_to_info = {}
    for entry, idx in info_to_idx.iteritems():
        idx_to_info[idx] = entry
    
    # let's do the actual writing
    # idx -> fpath
    output_fpath = os.path.join(output_dir, 'idx_to_fpath.txt')
    f = open(output_fpath, 'w')
    keys = sorted(idx_to_fpath.keys())
    for key in keys:
        print >> f, '%d\t%s' % (key, idx_to_fpath[key])
    f.close()

    # idx -> entry (e.g. idx -> email)
    output_fpath = os.path.join(output_dir, 'idx_to_info.txt')
    f = open(output_fpath, 'w')
    keys = sorted(idx_to_info.keys())
    for key in keys:
        print >> f, '%d\t%s' % (key, idx_to_info[key])
    f.close()

    # filepath idx -> list of indices to info e.g. to emails
    output_fpath = os.path.join(output_dir, 'fpathidx_to_infoidxlist.txt')    
    f = open(output_fpath, 'w')
    for key, value in fpathidx_to_infoidxlist.iteritems():
        print >> f, '%d' % key,
        for v in value:
            print >> f, '%d' % v,
        print >> f, ''
    f.close()


# In[ ]:



if __name__ == '__main__':
    # In[10]:

    # run parameters
    input_dir = '/home/klevin/emails'

    # this is the cumulative size of input_dir files starting
    # from smaller and going to larger-size ones
    cum_size_limit = 500000000
    output_dir = '/tmp/emails-500M'

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)


    # In[11]:

    # now let's run  

    meta_fname_list= pick_fnames(input_dir, cum_size_limit)

    fpath_to_idx, info_to_idx = generate_lookup_tables(input_dir, meta_fname_list)

    fpathidx_to_infoidxlist = generate_cross_lookup_table(input_dir, meta_fname_list, 
                                                          fpath_to_idx, info_to_idx)

    write_lookups(output_dir, fpath_to_idx, info_to_idx, fpathidx_to_infoidxlist)


    # In[ ]:



