import os
import math
import networkx as nx

def distance(P, Q):
    return math.sqrt(math.pow(Q[0]-P[0], 2) + math.pow(Q[1]-P[1], 2))

def reduce_avg(numbers):
    s = 0
    for n in numbers:
        s += n
    return s / len(numbers)

def reduce_any(l):
    return l[0]

REDUCE_STRING_MATCH = "iMM904"
def reduce_string(l):
    #print(reduce_string, l)
    v = None
    for s in l:
        if REDUCE_STRING_MATCH in s:
            v = s
    if v == None:
        return reduce_any(l)
    return v

def get_seed_ids(rxn):
    seed_ids = set()
    if '@' in rxn['id']:
        rxn_id, database = rxn['id'].split('@')
        seed_ids.add(rxn_id)
        if 'obsolete_seeds' in rxn:
            for rxn_id in rxn['obsolete_seeds']:
                rxn_id, database = rxn_id.split('@')
                seed_ids.add(rxn_id)
    else:
        if 'seed.reaction' in rxn['dblinks']:
            for rxn_id in rxn['dblinks']['seed.reaction']:
                seed_ids.add(rxn_id)
        if 'seed.obsolete' in rxn['dblinks']:
            for rxn_id in rxn['dblinks']['seed.obsolete']:
                seed_ids.add(rxn_id)
    return seed_ids

def get_cpd_seed_ids(model_metabolite):
    seed_ids = set()
    if '@' in model_metabolite['id']:
        seed_id, database = model_metabolite['id'].split('@')
        if database == 'SEED':
            seed_ids.add(seed_id)
            if 'obsolete_seeds' in model_metabolite:
                for seed_id in model_metabolite['obsolete_seeds']:
                    seed_id, database = seed_id.split('@')
                    seed_ids.add(seed_id)
    else:
        if 'cluster' in model_metabolite:
            for value in model_metabolite['cluster']:
                if '@' in value:
                    seed_id, database = value.split('@')
                    if database == 'SEED':
                        seed_ids.add(seed_id)
                else:
                    print('?', value)
    return seed_ids

class EscherModel:
    
    def __init__(self, escher_model):
        self.escher_model = escher_model
        self.update_index()
    
    def update_index(self):
        self.id_to_index = {}
        for i in range(len(self.escher_model['metabolites'])):
            metabolite = self.escher_model['metabolites'][i]
            self.id_to_index[metabolite['id']] = i
            
    def get_metabolite_by_id(self, id):
        if id in self.id_to_index:
            return self.escher_model['metabolites'][self.id_to_index[id]]
        return None
    
    def asdasd(self):
        name_to_ids = {}
        #id_dups = {}
        for m_o in escher_model_original['metabolites']:
            name_to_ids[m_o['name']] = []
            #id_dups[m_o['id']] = []
        for m_o in escher_model_original['metabolites']:
            name_to_ids[m_o['name']].append(m_o['id'])
            #id_dups[m_o['id']].append(m_o)
        for k in id_dups:
            if len(id_dups[k]) > 1:
                1
                #print(k, id_dups[k])
                
    def merge_compounds(self, u_alias, name, ids, mapper):
        ids_mapped = set()

        for database in ids:
            if database in mapper:
                for cpd_id in ids[database]:
                    ids_mapped.add(cpd_id + '@' + mapper[database])
            else:
                print('ignore:', database)

        #print(ids_mapped)

        to_merge = []
        databases = set()
        for m in self.escher_model['metabolites']:
            database = 'universal'
            if '@' in m['id']:
                cpd_id, database = m['id'].split('@')
            if u_alias == m['id']:
                print('alias already exists:', m)
                return
            if m['id'] in ids_mapped:
                to_merge.append(m)

        if len(to_merge) == 0:
            print('nothing to merge')
            return

        merge_compound = {
            'charge': 0,
            'compartment': 'default',
            'formula': to_merge[0]['formula'],
            'id': u_alias,
            'name': name,
            'notes': {},
            'cluster' : []
        }

        for m in to_merge:
            merge_compound['cluster'].append(m['id'])

        merge_compound

        #add merge_compound
        #delete to_merge
        metabolites = []
        for m in self.escher_model['metabolites']:
            if not m['id'] in ids_mapped:
                metabolites.append(m)
        self.escher_model['metabolites'] = metabolites
        metabolites.append(merge_compound)

        for r in self.escher_model['reactions']:
            swap = ids_mapped & set(r['metabolites'].keys())
            if not 'replaced_cpds' in r:
                r['replaced_cpds'] = {}
            for cpd_id in swap:
                v = r['metabolites'][cpd_id]
                del r['metabolites'][cpd_id]
                r['metabolites'][u_alias] = v
                r['replaced_cpds'][u_alias] = cpd_id
    
    def set_annotation(self, id, bios_entry, bios_database):
        for m in self.escher_model['metabolites']:
            if id == m['id']:
                if not 'bios_references' in m:
                    m['bios_references'] = {}
                m['bios_references'][bios_database] = bios_entry
    
    def detect_models(self):
        model_ids = set()
        for m in self.escher_model['metabolites']:
            id = m['id']
            if '@' in id:
                model_id = id.split('@')[1]
                model_ids.add(model_id)
            else:
                model_ids.add('none')
        return model_ids
    
    #map_to target id
    #search ids to change
    def merge_model_nodes(self, map_to, search):
        #for m in escher_model['metabolites']:
        #    if m['id'] in search:
        #        #m['id'] = map_to
        #        print(m['id'], m['name'], '->', map_to)
        for r in self.escher_model['reactions']:
            replace = {}
            changed = False
            for id in r['metabolites']:
                if id in search and not id == map_to:
                    replace[map_to] = r['metabolites'][id]
                    changed = True
                else:
                    replace[id] = r['metabolites'][id]
            if changed:
                #print(r['id'], replace)
                r['metabolites'] = replace
                
    def merge_metabolites(self, keep, ids):
        if not keep in ids:
            print(keep, 'not in', ids)
            return None
        primary = self.get_metabolite_by_id(keep)
        if not 'bios_models' in primary:
            primary['bios_models'] = []
        primary['bios_models'].extend(ids)
        primary['bios_models'] = list(set(primary['bios_models']))
        to_delete = set()
        for id in ids:
            if not id == keep and id in self.id_to_index:
                to_delete.add(id)
            else:
                print('keep/skip:', id)

        self.delete_metabolites(to_delete)
        self.merge_model_nodes(keep, ids)
        return primary
    
    def delete_metabolites(self, ids):
        metabolites = []
        for m in self.escher_model['metabolites']:
            if not m['id'] in ids:
                metabolites.append(m)
        print('deleted', len(self.escher_model['metabolites']) - len(metabolites))
        self.escher_model['metabolites'] = metabolites
        self.update_index()
                
    def get_metabolite_groups(self):
        groups = {}
        for m in self.escher_model['metabolites']:
            bios_id = m['bios_id']
            m_id = m['id']
            if not m_id in groups:
                groups[m_id] = set()
            groups[m_id].add(bios_id)
        for i in groups:
            if len(groups[i]) > 1:
                #print(i, groups[i])
                model_count = {}
                for bios_id in groups[i]:
                    model_id = bios_id.split('@')[1]
                    if not model_id in model_count:
                        model_count[model_id] = 0
                    model_count[model_id] += 1
                    m = self.escher_model['metabolites'][bios_id_to_node_index[bios_id]]
                    bios_references = None
                    if 'bios_references' in m:
                        bios_references = m['bios_references']
                    if bios_references == None:
                        #print(i, bios_id_to_node_index[bios_id], bios_id, m['name'], bios_references)
                        1
                for model_id in model_count:
                    if model_count[model_id] > 1:
                        print(i, groups[i])
                        break
        return groups
    
    def initialize_bios_ids(self):
        for m in self.escher_model['metabolites']:
            m['bios_id'] = m['id']
        for r in self.escher_model['reactions']:
            r['bios_id'] = r['id']
            
    def map_escher_model_data(self, cpd_map_to_model, rxn_map_to_model):
        seed_match = set(rxn_map_to_model)
        rxn_remap = {}
        for model_reaction in self.escher_model['reactions']:
            seed_ids = get_seed_ids(model_reaction)
            match = seed_match & seed_ids
            if len(match) == 1:
                rxn_remap[model_reaction['id']] = rxn_map_to_model[match.pop()]
                #print(seed_ids, rxn_remap[model_reaction['id']])
            elif len(match) > 1:
                print('error', match, seed_ids)

        seed_match = set(cpd_map_to_model)
        cpd_remap = {}
        for model_metabolite in self.escher_model['metabolites']:
            seed_ids = get_cpd_seed_ids(model_metabolite)

            match = seed_match & seed_ids
            if len(match) == 1:
                cpd_remap[model_metabolite['id']] = cpd_map_to_model[match.pop()]
            elif len(match) > 1:
                cpd_remap[model_metabolite['id']] = cpd_map_to_model[sorted(match)[0]]
                print('error', match, seed_ids)
        return cpd_remap, rxn_remap

class EscherMap:
    
    def __init__(self, escher_map):
        self.escher_map = escher_map
        self.escher_graph = escher_map[1]
        self.escher_data = escher_map[0]
        
    def swap_ids(self, cpd_remap, rxn_remap):
        for map_uid in self.escher_graph['nodes']:
            node = self.escher_graph['nodes'][map_uid]
            if node['node_type'] == 'metabolite' and node['bigg_id'] in cpd_remap:
                node['bigg_id'] = cpd_remap[node['bigg_id']]
        for map_uid in self.escher_graph['reactions']:
            map_reaction = self.escher_graph['reactions'][map_uid]
            if map_reaction['bigg_id'] in rxn_remap:
                map_reaction['bigg_id'] = rxn_remap[map_reaction['bigg_id']]
            for m in map_reaction['metabolites']:
                if m['bigg_id'] in cpd_remap:
                    m['bigg_id'] = cpd_remap[m['bigg_id']]
            
class EscherCuration:
    
    def __init__(self, escher_model, escher_map):
        self.escher_model = escher_model
        self.escher_map = escher_map
        self.escher_graph = escher_map[1]
        self.em = EscherModel(escher_model)
    
    def get_rxn_coordinates(self, escher_reaction):
        for segment_id in escher_reaction['segments']:
            segment = escher_reaction['segments'][segment_id]
            src_id = segment['from_node_id']
            dst_id = segment['to_node_id']
            src_node = self.escher_graph['nodes'][src_id]
            dst_node = self.escher_graph['nodes'][dst_id]
            if src_node['node_type'] == 'midmarker':
                return (src_node['x'], src_node['y'])
            if dst_node['node_type'] == 'midmarker':
                return (dst_node['x'], dst_node['y'])
            #print(segment_id, src_id, dst_id, src_node['node_type'], dst_node['node_type'])
        return (0, 0)
    
    def get_escher_reaction_metabolites(self, escher_reaction):
        metabolties = set()
        for segment_id in escher_reaction['segments']:
            segment = escher_reaction['segments'][segment_id]
            src_id = segment['from_node_id']
            dst_id = segment['to_node_id']
            src_node = self.escher_graph['nodes'][src_id]
            dst_node = self.escher_graph['nodes'][dst_id]
            if src_node['node_type'] == 'metabolite':
                metabolties.add(src_node['bigg_id'])
            if dst_node['node_type'] == 'metabolite':
                metabolties.add(dst_node['bigg_id'])
        return metabolties
    
    def get_reaction_id_from_marker_id(self, marker_id):
        for i in self.escher_graph['reactions']:
            escher_reaction = self.escher_graph['reactions'][i]
            for segment_id in escher_reaction['segments']: 
                segment = escher_reaction['segments'][segment_id]
                src_id = segment['from_node_id']
                dst_id = segment['to_node_id']
                if src_id == marker_id:
                    return i
                if dst_id == marker_id:
                    return i
        return None
    
    def translate_map(self, map_json, out_name, out_json):
        escher_map = None
        with open(map_json, 'r') as f:
            data = f.read()
            escher_map = json.loads(data)
        escher_graph = escher_map[1]
        #ec = EscherCuration(escher_model, escher_map)
        #print(ec.escher_map[1].keys())

        swap_name = {}
        swap = {}
        for m in self.em.escher_model['metabolites']:
            if 'cluster' in m:
                for cpd_id in m['cluster']:
                    swap[cpd_id] = m['id']
                swap_name[m['id']] = m['name']
        print(len(swap))
        print(len(swap_name))

        for node_id in escher_graph['nodes']:
            node = escher_graph['nodes'][node_id]
            if node['node_type'] == 'metabolite' and node['bigg_id'] in swap:
                node['original_id'] = node['bigg_id']
                node['bigg_id'] = swap[node['bigg_id']]
                node['name'] = swap_name[node['bigg_id']]

        for reaction_id in escher_graph['reactions']:
            reaction = escher_graph['reactions'][reaction_id]
            for m in reaction['metabolites']:
                if m['bigg_id'] in swap:
                    m['original_id'] = m['bigg_id']
                    m['bigg_id'] = swap[m['bigg_id']]

        escher_map[0]['map_name'] = out_name

        with open(out_json, 'w') as f:
            f.write(json.dumps(escher_map))

        return escher_map, swap, swap_name
    
    def merge_nodes(self, ids):
        reduce_func = {
            'x' : reduce_avg,
            'y' : reduce_avg,
            'label_x' : reduce_avg,
            'label_y' : reduce_avg,
            'bigg_id' : reduce_string
        }

        consensus_data = {}
        for node_id in ids:
            if node_id in self.escher_graph['nodes']:
                node = self.escher_graph['nodes'][node_id]
                for k in node.keys():
                    if not k in consensus_data:
                        consensus_data[k] = []
                    #print(node_id, k, node[k])
                    consensus_data[k].append(node[k])
            else:
                print('not found:', node_id)
                
        #print(consensus_data)
        merge_node = {}
        for k in consensus_data:
            #print(k)
            if k in reduce_func:
                merge_node[k] = reduce_func[k](consensus_data[k])
            else:
                merge_node[k] = reduce_any(consensus_data[k])
                
        #print(consensus_data)
        merge_node['bios_species'] = consensus_data['bigg_id']
        merge_node['name'] += " " + '#'.join(merge_node['bios_species'])
        #print(merge_node)

        return ids[0], merge_node
    
    def get_cluster_old(self, id):
        cluster = set([id])
        node = escher_graph['nodes'][id]
        coords_1 = (node['x'], node['y'])
        for node_id in escher_graph['nodes']:
            if not node_id == id and node_type[node_id] == 'metabolite':
                other_node = escher_graph['nodes'][node_id]
                coords_2 = (other_node['x'], other_node['y'])
                dist = distance(coords_1, coords_2)
                if dist < 100:
                    cluster.add(node_id)
                    #print(node_id, dist, other_node['bigg_id'])
        return list(cluster)

    def get_cluster(self, coords_1, max_distance, type_match):
        cluster = set()
        for node_id in self.escher_graph['nodes']:
            node = self.escher_graph['nodes'][node_id]
            if node['node_type'] == type_match:
                other_node = node
                coords_2 = (other_node['x'], other_node['y'])
                dist = distance(coords_1, coords_2)
                if dist < max_distance:
                    cluster.add(node_id)
                    #print(node_id, dist, other_node['bigg_id'])
        return cluster
    
    def compute_all_metabolite_clusters(self, max_distance=100):
        g = nx.Graph()
        for node_id in self.escher_graph['nodes']:
            node = self.escher_graph['nodes'][node_id]
            if not node_id in g.nodes and node['node_type'] == 'metabolite':
                node = self.escher_graph['nodes'][node_id]
                coords_1 = (node['x'], node['y'])
                cluster = self.get_cluster(coords_1, max_distance, 'metabolite')
                cluster = list(cluster)
                if len(cluster) > 1:
                    prev = cluster[0]
                    for i in range(len(cluster) - 1):
                        g.add_edge(prev, cluster[i + 1])

        cc = list(nx.algorithms.connected_components(g))
        return cc
    
    def compute_identifiers_merge_from_clusters(self, clusters):
        g_ids = nx.Graph()
        for c in clusters:
            cluster = list(c)
            prev = self.escher_graph['nodes'][cluster[0]]['bigg_id']
            for i in range(len(cluster) - 1):
                bigg = self.escher_graph['nodes'][cluster[i + 1]]['bigg_id']
                g_ids.add_edge(prev, bigg)
        cc_model_species = list(nx.algorithms.connected_components(g_ids))
        return cc_model_species
    
    def graph_reaction_replace(self, from_id, to_id):
        for escher_reaction_id in self.escher_graph['reactions']:
            escher_reaction = self.escher_graph['reactions'][escher_reaction_id]
    
    def merge_graph_nodes(self, merge_ids):
        merge_to, merge_node = self.merge_nodes(merge_ids)

        #delete all merged ids
        for id in merge_ids:
            if id in self.escher_graph['nodes']:
                print('delete node', id)
                del self.escher_graph['nodes'][id]
        #create the merged node
        self.escher_graph['nodes'][merge_to] = merge_node
        
        
        for escher_reaction_id in self.escher_graph['reactions']:
            escher_reaction = self.escher_graph['reactions'][escher_reaction_id]

            seqment_change = False
            for segment_id in escher_reaction['segments']:
                segment = escher_reaction['segments'][segment_id]
                from_node_id = segment['from_node_id']
                if from_node_id in merge_ids:
                    seqment_change = True
                    #print(from_node_id, '->', merge_to)
                    segment['from_node_id'] = merge_to
                to_node_id = segment['to_node_id']
                if to_node_id in merge_ids:
                    seqment_change = True
                    #print(to_node_id, '->', merge_to)
                    segment['to_node_id'] = merge_to
            if seqment_change:
                for m in escher_reaction['metabolites']:
                    if m['bigg_id'] in merge_node['bios_species']:
                        m['bigg_id'] = merge_node['bigg_id']
                        
    def get_graph_reaction(self, rxn_id):
        for rxn_index in self.escher_graph['reactions']:
            escher_reaction_ = self.escher_graph['reactions'][rxn_index]
            bigg_id = escher_reaction_['bigg_id']
            if bigg_id == rxn_id:
                return escher_reaction_
            
        return None
    
    
    def merge_reactions(self, keep, ids):
        to_delete_nodes = set()
        to_delete_reactions = set()
        merged = set()
        for rxn_index in ids:
            escher_reaction = self.escher_graph['reactions'][rxn_index]
            bigg_id = escher_reaction['bigg_id']
            merged.add(bigg_id)
            if not bigg_id == keep:
                for segment_id in escher_reaction['segments']: 
                    segment = escher_reaction['segments'][segment_id]
                    src_id = segment['from_node_id']
                    dst_id = segment['to_node_id']
                    if src_id in self.escher_graph['nodes']:
                        src_node = self.escher_graph['nodes'][src_id]
                        if not src_node['node_type'] == 'metabolite':
                            to_delete_nodes.add(src_id)
                    if dst_id in self.escher_graph['nodes']:
                        dst_node = self.escher_graph['nodes'][dst_id]
                        if not dst_node['node_type'] == 'metabolite':
                            to_delete_nodes.add(dst_id)
                    #print(rxn_index, bigg_id, src_id, src_node['node_type'])
                    #print(rxn_index, bigg_id, dst_id, dst_node['node_type'])
                to_delete_reactions.add(rxn_index)
        return merged, to_delete_nodes, to_delete_reactions
    
    def merge_graph_reaction_nodes(self, rxn_id):
        escher_reaction = self.get_graph_reaction(rxn_id)
        
        if escher_reaction == None:
            return None

        coords_1 = self.get_rxn_coordinates(escher_reaction)
        cluster = self.get_cluster(coords_1, 100, 'midmarker')
        if len(cluster) < 2:
            return None
        
        max_size = 0
        rxn_metabolites = {}
        rxn_ids = set()
        for marker_id in cluster:
            escher_reaction_id = self.get_reaction_id_from_marker_id(marker_id)
            rxn_ids.add(escher_reaction_id)
            escher_reaction = self.escher_graph['reactions'][escher_reaction_id]
            metabolites = self.get_escher_reaction_metabolites(escher_reaction)
            if len(metabolites) > max_size:
                max_size = len(metabolites)
            rxn_metabolites[escher_reaction['bigg_id']] = metabolites
            #print(escher_reaction_id, escher_reaction['bigg_id'], metabolites)

        valid = True
        pivot = None
        for rxn_id in rxn_metabolites:
            if len(rxn_metabolites[rxn_id]) == max_size:
                for other_id in rxn_metabolites:
                    set1 = rxn_metabolites[rxn_id]
                    set2 = rxn_metabolites[other_id]
                    diff = set2 - set1
                    if not len(diff) == 0:
                        valid = False
                    else:
                        pivot = rxn_id

        if valid:
            merged, del_nodes, del_reactions = self.merge_reactions(pivot, rxn_ids)
            print(valid, pivot, coords_1, cluster, merged)
            print(del_nodes, del_reactions)
            for rxn_index in rxn_ids:
                escher_reaction = self.escher_graph['reactions'][rxn_index]
                bigg_id = escher_reaction['bigg_id']
                print(rxn_id, bigg_id, pivot)
                for reaction in self.escher_model['reactions']:
                    if reaction['id'] == bigg_id:
                        reaction['id'] = pivot
                        break
            for node_id in del_nodes:
                del self.escher_graph['nodes'][node_id]
            for reaction_id in del_reactions:
                del self.escher_graph['reactions'][reaction_id]
                
def sync_graph():
    for node_id in ec.escher_graph['nodes']:
        node = ec.escher_graph['nodes'][node_id]
        if node['node_type'] == 'metabolite':            
            metabolite = em.get_metabolite_by_id(node['bigg_id'])
            if metabolite == None:
                swap = None
                for m in em.escher_model['metabolites']:
                    if 'bios_models' in m and node['bigg_id'] in m['bios_models']:
                        swap = (node['bigg_id'], m['id'])
                        node['bigg_id'] = m['id']
                print('swap', swap)
                if not swap == None:
                    for escher_reaction_id in ec.escher_graph['reactions']:
                        escher_reaction = ec.escher_graph['reactions'][escher_reaction_id]
                        for o in escher_reaction['metabolites']:
                            if swap[0] in o['bigg_id']:
                                o['bigg_id'] = swap[1]
                                
def get_clusterss(ec, em, any_merge = True):
    clusters = ec.compute_all_metabolite_clusters(max_distance=50)
    model_ids = em.detect_models()
    clusters_ = list()
    for cluster in clusters:
        ids = set()
        models = set()
        biggs = set()
        for id in cluster:
            ids.add(id)
            bigg_id = ec.escher_graph['nodes'][id]['bigg_id']
            biggs.add(bigg_id)
            if '@' in bigg_id:
                model_id = bigg_id.split('@')[1]
                models.add(model_id)
            else:
                models.add('none')
        #print(biggs)

        if any_merge or model_ids == models or len(biggs & set(id_filter)) > 0:
            #keep_id, merge_node = ec.merge_nodes(list(ids))
            #print(ids)
            clusters_.append(ids)
            #print(keep_id, merge_node)
    clusters = clusters_
    cpd_merges = ec.compute_identifiers_merge_from_clusters(clusters)
    
    return cpd_merges