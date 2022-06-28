import click


class RequiredIf(click.Option):
    """Make options required if other optional option is set to the specified
    value.
    """

    def __init__(self, *args, **kwargs):
        self.required_if: dict = kwargs.pop('required_if')
        self.required_if_info = ' or '.join(
            [f'{key}={value}' for key, value in self.required_if.items()]
        )

        assert self.required_if, '"required_if" parameter is required'
        kwargs['help'] = (
            f'{kwargs.get("help", "")}  Note: This option is required'
            f' with "{self.required_if_info}"'
        ).strip()

        super(RequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        current_opt = self.consume_value(ctx, opts)

        for other_param in ctx.command.get_params(ctx):
            if other_param is self:
                continue

            name_present = (other_param.human_readable_name
                            in self.required_if.keys())
            if name_present:
                value_present = (
                        other_param.consume_value(ctx, opts)[0]
                        == self.required_if[other_param.human_readable_name]
                )
                if value_present:
                    if not current_opt[0]:
                        raise click.UsageError(
                            f'Illegal Usage:'
                            f' Option {self.get_error_hint(ctx)} is required'
                            f' with "{self.required_if_info}"'
                        )

        return super(RequiredIf, self).handle_parse_result(ctx, opts, args)
