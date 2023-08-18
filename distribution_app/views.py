from django.shortcuts import render, redirect


def get_info(request):

    if request.method == 'GET':

        return render(
            request=request,
            template_name='distribution_app/index.html'
        )

    if request.method == 'POST':

        cash = float(request.POST.get('cash'))
        creditors_amount = int(request.POST.get('amount'))

        request.session['cash'] = cash
        request.session['creditors_amount'] = creditors_amount

        return redirect(
            to='creditors_info'
        )


def get_creditors_info(request):

    if request.method == 'GET':

        if 'cash' not in request.session or 'creditors_amount' not in request.session:
            return render(
                request=request,
                template_name='errors/access_error.html'
            )

        context = {
            'cash': request.session.get('cash'),
            'creditors_amount': request.session.get('creditors_amount'),
            'creditors_range': range(request.session.get('creditors_amount'))
        }

        return render(
            request=request,
            template_name='distribution_app/creditors_info.html',
            context=context
        )

    if request.method == 'POST':

        cash = float(request.POST.get('cash'))
        creditors_amount = int(request.POST.get('amount'))
        creditors = []

        for i in range(creditors_amount):
            creditor = {
                'name': request.POST.get(f'creditor_{i}_name'),
                'value': float(request.POST.get(f'creditor_{i}_value')),
                'is_percent': bool(request.POST.get(f'creditor_{i}_is_percent')),
                'percent_or_fee': float(request.POST.get(f'creditor_{i}_percent_or_fee'))
            }
            creditors.append(creditor)

        request.session['creditors'] = creditors
        request.session['cash'] = cash
        request.session['creditors_amount'] = creditors_amount

        return redirect(
            to='results'
        )


def show_results(request):
    if request.method == 'GET':
        if 'creditors' not in request.session and 'cash' not in request.session:
            return render(
                request=request,
                template_name='errors/access_error.html'
            )

        cash = request.session.get('cash')
        creditors = request.session.get('creditors')

        context = calculate(cash, creditors)
        context['cash'] = cash
        context['creditors'] = creditors

        return render(
            request=request,
            template_name='distribution_app/results.html',
            context=context
        )


def calculate(cash, inp_creditors):
    creditors = {
        creditor['name']: float(creditor['value'])
        for creditor in inp_creditors
    }
    conditions = {
        creditor['name']: {
            'is_percent': creditor['is_percent'],
            'percent_or_fee': float(creditor['percent_or_fee'])
        }
        for creditor in inp_creditors
    }

    total_fees = {}

    debt = sum(creditors.values())
    ratio = {name: value / debt * 100 for name, value in creditors.items()}

    creditors_get = {}
    bank_payments = {}

    sum_fee = 0
    for creditor, condition in conditions.items():
        if not condition['is_percent']:
            sum_fee += condition['percent_or_fee']

    sum_percent = 100
    for creditor, condition in conditions.items():
        if condition['is_percent']:
            sum_percent += ratio[creditor] / 100 * condition['percent_or_fee']

    if sum_fee > cash:
        remaining_cash = 0
    else:
        remaining_cash = cash - sum_fee

    for name, value in ratio.items():
        temp = remaining_cash / sum_percent * value
        creditors_get[name] = temp
        if conditions[name]['is_percent']:
            bank_payments[name] = temp + temp / 100 * conditions[name]['percent_or_fee']
            total_fees[name] = temp / 100 * conditions[name]['percent_or_fee']
        else:
            bank_payments[name] = temp + conditions[name]['percent_or_fee']
            total_fees[name] = conditions[name]['percent_or_fee']

    return {
        'total_debt': sum(creditors.values()),
        'total_creditors_get': sum(creditors_get.values()),
        'creditors': creditors,
        'ratio': ratio,
        'creditors_get': creditors_get,
        'bank_payments': bank_payments,
        'total_fees': total_fees
    }


def about(request):
    return render(
        request=request,
        template_name='distribution_app/about.html'
    )
