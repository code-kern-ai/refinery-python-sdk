def get_label_names(_label):
    label_manual = f"{_label}__MANUAL"
    label_weakly_supervised = f"{_label}__WEAK_SUPERVISION"
    return label_manual, label_weakly_supervised


def split_train_test_on_weak_supervision(client, _input, _label):

    label_manual, label_weakly_supervised = get_label_names(_label)
    manual_data = client.get_record_export(
        tokenize=False,
        keep_attributes=[_input, label_manual],
        dropna=True,
    ).rename(columns={label_manual: "label"})

    weakly_supervised_data = client.get_record_export(
        tokenize=False,
        keep_attributes=[_input, label_weakly_supervised],
        dropna=True,
    ).rename(columns={label_weakly_supervised: "label"})

    weakly_supervised_data = weakly_supervised_data.drop(manual_data.index)

    labels = list(
        set(
            manual_data.label.unique().tolist()
            + weakly_supervised_data.label.unique().tolist()
        )
    )

    return (
        manual_data.reset_index(drop=True),
        weakly_supervised_data.reset_index(drop=True),
        labels,
    )
