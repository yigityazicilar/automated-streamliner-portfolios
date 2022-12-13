def formulate(eprime_model, eprime_param, solver, raw_instance):
    sr_output_file = solver.get_savilerow_output_file(eprime_model, raw_instance)
    solver_flag = solver.get_savilerow_flag()
    command = ['savilerow', '-in-param', eprime_param, '-in-eprime', eprime_model,
               '-num-solutions', '1', f'-{solver_flag}', f'{solver.get_savilerow_output_flag()}', f'{sr_output_file}',
               '-preprocess', 'None']
    return command


def parse_std_out(out, instance_stats):
    return


def parse_std_err(out, instance_stats):
    return
