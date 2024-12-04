import pandas as pd

df = pd.read_csv('dsc540_df_train.csv')

def get_top_corrs(df):
    threshold = 0.4
    i = 0
    pairs = set()
    result = pd.DataFrame()
    orig_corr = df.corr()
    c = orig_corr.abs()
    so = c.unstack()

    corrl8r_vars = dict()
    high_corr_attrs = []

    print(f'Unique pairs of attributes with correlation > {threshold}):\n')
    print(f'Pair{" "*53}Correlation value')
    for index, value in so.sort_values(ascending=False).items():
        if value > threshold \
        and index[0] != index[1] \
        and (index[0], index[1]) not in pairs \
        and (index[1], index[0]) not in pairs:
            alpha_sorted_pair = sorted([index[0], index[1]])
            pairs.add(index)
            high_corr_attrs.append
            result.loc[i, ['Variable 1', 'Variable 2', 'Correlation Coefficient']] = [alpha_sorted_pair[0], alpha_sorted_pair[1], orig_corr.loc[(index[0], index[1])]]
            i += 1
            og_value = orig_corr.loc[(alpha_sorted_pair[0], alpha_sorted_pair[1])]
            formatted_attribute_pair = f'{alpha_sorted_pair[0]} & {alpha_sorted_pair[1]}'
            attr_pair_str_len = len(formatted_attribute_pair)
            print_buffer = (56 - attr_pair_str_len) * ' '
            print(f'{formatted_attribute_pair}:{print_buffer}{round(og_value, 4)}')

            if index[0] not in corrl8r_vars:
                corrl8r_vars[index[0]] = ([index[1]], [og_value])
            else:
                corrl8r_vars[index[0]][0].append(index[1])
                corrl8r_vars[index[0]][1].append(og_value)

            if index[1] not in corrl8r_vars:
                corrl8r_vars[index[1]] = ([index[0]], [og_value])
            else:
                corrl8r_vars[index[1]][0].append(index[0])
                corrl8r_vars[index[1]][1].append(og_value)
            


    print(f'\n\nVariables correlated above {threshold} :\n')

    attrs_corrl8d_above_threshold = sorted(corrl8r_vars.keys())

    # print(df[attrs_corrl8d_above_threshold].corr())

    df_high_corrs = df[df[attrs_corrl8d_above_threshold].corr() > 0.4]

    print(df_high_corrs)

    print('\n\nNEW SECTION TESTING\n')

    print(corrl8r_vars)
    correlated_groups = set()
    for pair in corrl8r_vars.items():
        curr_group = set()
        curr_group.add(pair[0])
        for attr in pair[1][0]:
            curr_group.add(attr)
        frozen_curr_group = frozenset(curr_group)
        correlated_groups.add(frozen_curr_group)
    
    for group in correlated_groups:
        print(group)






get_top_corrs(df.iloc[:, :-1])
