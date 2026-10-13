"""Derive displayed telemetry from actual MMIO writes in the virtual model."""
import math

def effects(lab,state):
    mmio=state.get('mmio',{});values=[mmio.get(str(0xf000+i*4),0) for i in range(3)]
    model={'component':lab.component,'values':values}
    if lab.system.slug=='quantum':
        model['configuration_valid']=values[0] in range(4) and values[1]==2 and values[2]>0
        if not model['configuration_valid']:
            model['note']='Invalid profile: use mask 0-3, exactly two qubits and a positive requested shot count. No physical QPU controlled.'
            return model
        amplitudes=[1.0,0.0,0.0,0.0]
        if values[0]&1:
            amplitudes=[(amplitudes[0]+amplitudes[1])/math.sqrt(2),(amplitudes[0]-amplitudes[1])/math.sqrt(2),
                        (amplitudes[2]+amplitudes[3])/math.sqrt(2),(amplitudes[2]-amplitudes[3])/math.sqrt(2)]
        if values[0]&2:amplitudes[1],amplitudes[3]=amplitudes[3],amplitudes[1]
        model['probabilities']={f'{i:02b}':round(a*a,6) for i,a in enumerate(amplitudes)}
        model['note']='Exact ideal-state probabilities. No shots sampled and no physical QPU controlled.'
    else:
        enable_index=1 if lab.system.slug=='pc' and lab.component=='ram' else 2
        model['enabled']=values[enable_index]==1
    if lab.system.slug=='satellite' and lab.component=='antenna':
        model['computed_parity']=(values[0]&255).bit_count()%2;model['parity_matches']=model['computed_parity']==values[1]
    elif lab.system.slug=='satellite':model['payload_bytes_per_second']=values[0]*values[1]
    elif lab.system.slug=='data-center' and lab.component=='cooling':model['headroom_watts']=values[1]-values[0]
    elif lab.system.slug=='data-center':model['distinct_node_placement_possible']=0<values[1]<=values[0]
    elif lab.system.slug=='supercomputer' and lab.component=='cpu':model['requested_workers']=values[0]*values[1]
    return model
