# Generated by Django 5.2.1 on 2025-05-16 03:29

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccountingClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('code', models.CharField(help_text='Unique class code (1-9)', max_length=1, unique=True, verbose_name='code')),
                ('name', models.CharField(help_text='The name of the accounting class', max_length=255, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Accounting Class',
                'verbose_name_plural': 'Accounting Classes',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='AccountingJournal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('id_journal', models.CharField(help_text='Unique journal identifier', max_length=10, unique=True, verbose_name='journal ID')),
                ('code', models.CharField(help_text='Journal code', max_length=3, verbose_name='code')),
                ('short_name', models.CharField(help_text='Short name/description of the journal', max_length=10, verbose_name='short name')),
                ('name', models.CharField(help_text='Full name of the journal', max_length=255, verbose_name='name')),
                ('is_opening_balance', models.BooleanField(default=False, help_text='Whether this journal is used for opening balance entries', verbose_name='is opening balance')),
                ('company_code', models.CharField(blank=True, help_text='Company code associated with this journal', max_length=10, null=True, verbose_name='company code')),
            ],
            options={
                'verbose_name': 'Accounting Journal',
                'verbose_name_plural': 'Accounting Journals',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='AccountingType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('code', models.CharField(help_text='Unique code for the accounting type', max_length=3, unique=True, verbose_name='code')),
                ('short_name', models.CharField(help_text='Short name of the accounting type', max_length=50, verbose_name='short name')),
                ('full_name', models.CharField(help_text='Full name of the accounting type', max_length=255, verbose_name='full name')),
                ('nature', models.CharField(blank=True, help_text='Nature of the accounting type', max_length=50, null=True, verbose_name='nature')),
            ],
            options={
                'verbose_name': 'Accounting Type',
                'verbose_name_plural': 'Accounting Types',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='FiscalYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('year', models.PositiveIntegerField(help_text='The numeric year (e.g., 2023)', unique=True, verbose_name='year')),
                ('name', models.CharField(help_text='Name of the fiscal year', max_length=255, verbose_name='name')),
                ('start_date', models.DateField(help_text='Start date of the fiscal year', verbose_name='start date')),
                ('end_date', models.DateField(help_text='End date of the fiscal year', verbose_name='end date')),
                ('is_closed', models.BooleanField(default=False, help_text='Whether the fiscal year is closed for posting', verbose_name='is closed')),
                ('is_current', models.BooleanField(default=False, help_text='Whether this is the current fiscal year', verbose_name='is current')),
            ],
            options={
                'verbose_name': 'Fiscal Year',
                'verbose_name_plural': 'Fiscal Years',
                'ordering': ['-year'],
            },
        ),
        migrations.CreateModel(
            name='AccountingChapter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('code', models.CharField(help_text='Unique chapter code (e.g., 10, 11)', max_length=2, unique=True, verbose_name='code')),
                ('name', models.CharField(help_text='The name of the accounting chapter', max_length=255, verbose_name='name')),
                ('accounting_class', models.ForeignKey(help_text='The accounting class this chapter belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='chapters', to='accounting.accountingclass')),
            ],
            options={
                'verbose_name': 'Accounting Chapter',
                'verbose_name_plural': 'Accounting Chapters',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='AccountingEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('entry_number', models.CharField(help_text='Unique identifier for the entry', max_length=50, unique=True, verbose_name='entry number')),
                ('entry_date', models.DateField(help_text='Date of the accounting entry', verbose_name='entry date')),
                ('posting_date', models.DateField(blank=True, help_text='Date when the entry was posted to ledger', null=True, verbose_name='posting date')),
                ('reference', models.CharField(blank=True, help_text='Reference or description for this entry', max_length=100, verbose_name='reference')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('validated', 'Validated'), ('posted', 'Posted'), ('cancelled', 'Cancelled')], default='draft', help_text='Current status of the accounting entry', max_length=20, verbose_name='status')),
                ('is_opening_balance', models.BooleanField(default=False, help_text='Whether this is an opening balance entry', verbose_name='is opening balance')),
                ('is_closing_entry', models.BooleanField(default=False, help_text='Whether this is a closing entry', verbose_name='is closing entry')),
                ('source_document', models.CharField(blank=True, help_text='The source document that triggered this entry', max_length=255, null=True, verbose_name='source document')),
                ('source_document_id', models.CharField(blank=True, help_text='The ID of the source document', max_length=100, null=True, verbose_name='source document ID')),
                ('is_reversing_entry', models.BooleanField(default=False, help_text='Whether this is a reversing entry', verbose_name='is reversing entry')),
                ('original_entry', models.ForeignKey(blank=True, help_text='The original entry that this entry reverses', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reversing_entries', to='accounting.accountingentry')),
                ('journal', models.ForeignKey(help_text='The journal in which this entry is recorded', on_delete=django.db.models.deletion.PROTECT, related_name='entries', to='accounting.accountingjournal')),
                ('fiscal_year', models.ForeignKey(help_text='The fiscal year this entry belongs to', on_delete=django.db.models.deletion.PROTECT, related_name='entries', to='accounting.fiscalyear')),
            ],
            options={
                'verbose_name': 'Accounting Entry',
                'verbose_name_plural': 'Accounting Entries',
                'ordering': ['-entry_date', '-entry_number'],
            },
        ),
        migrations.CreateModel(
            name='AccountingSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('code', models.CharField(help_text='Unique section code (e.g., 101, 106)', max_length=3, unique=True, verbose_name='code')),
                ('name', models.CharField(help_text='The name of the accounting section', max_length=255, verbose_name='name')),
                ('chapter', models.ForeignKey(help_text='The accounting chapter this section belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='accounting.accountingchapter')),
            ],
            options={
                'verbose_name': 'Accounting Section',
                'verbose_name_plural': 'Accounting Sections',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='GeneralLedgerAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('account_number', models.CharField(help_text='Unique account number', max_length=6, unique=True, verbose_name='account number')),
                ('short_name', models.CharField(help_text='Abbreviated account name', max_length=50, verbose_name='short name')),
                ('full_name', models.CharField(help_text='Complete account name', max_length=255, verbose_name='full name')),
                ('is_balance_sheet', models.BooleanField(default=True, help_text="True if this is a balance sheet account, False if it's an income statement account", verbose_name='is balance sheet')),
                ('budget_account_code', models.CharField(blank=True, max_length=20, null=True, verbose_name='budget account code')),
                ('recovery_status', models.CharField(blank=True, max_length=50, null=True, verbose_name='recovery status')),
                ('financial_statement_group', models.CharField(blank=True, max_length=50, null=True, verbose_name='financial statement group')),
                ('section', models.ForeignKey(blank=True, help_text='The accounting section this account belongs to', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='accounting.accountingsection')),
            ],
            options={
                'verbose_name': 'General Ledger Account',
                'verbose_name_plural': 'General Ledger Accounts',
                'ordering': ['account_number'],
            },
        ),
        migrations.CreateModel(
            name='AccountingEntryLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('line_number', models.PositiveIntegerField(help_text='Line number within the entry', verbose_name='line number')),
                ('description', models.CharField(blank=True, help_text='Description of the accounting line', max_length=255, verbose_name='description')),
                ('is_debit', models.BooleanField(help_text='Whether this is a debit (True) or credit (False) line', verbose_name='is debit')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Amount for this line', max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='amount')),
                ('auxiliary_account_id', models.CharField(blank=True, help_text='ID of the auxiliary account (e.g., supplier, customer)', max_length=50, null=True, verbose_name='auxiliary account ID')),
                ('entry', models.ForeignKey(help_text='The parent accounting entry', on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='accounting.accountingentry')),
                ('auxiliary_account_type', models.ForeignKey(blank=True, help_text='Type of auxiliary account if applicable', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='entry_lines', to='accounting.accountingtype')),
                ('account', models.ForeignKey(help_text='The general ledger account for this line', on_delete=django.db.models.deletion.PROTECT, related_name='entry_lines', to='accounting.generalledgeraccount')),
            ],
            options={
                'verbose_name': 'Accounting Entry Line',
                'verbose_name_plural': 'Accounting Entry Lines',
                'ordering': ['entry', 'line_number'],
            },
        ),
        migrations.AddIndex(
            model_name='accountingentry',
            index=models.Index(fields=['entry_date'], name='accounting__entry_d_c649e5_idx'),
        ),
        migrations.AddIndex(
            model_name='accountingentry',
            index=models.Index(fields=['fiscal_year'], name='accounting__fiscal__b9086e_idx'),
        ),
        migrations.AddIndex(
            model_name='accountingentry',
            index=models.Index(fields=['journal'], name='accounting__journal_ed18de_idx'),
        ),
        migrations.AddIndex(
            model_name='accountingentry',
            index=models.Index(fields=['status'], name='accounting__status_af48a1_idx'),
        ),
        migrations.AddIndex(
            model_name='accountingentryline',
            index=models.Index(fields=['account'], name='accounting__account_b103a0_idx'),
        ),
        migrations.AddIndex(
            model_name='accountingentryline',
            index=models.Index(fields=['entry'], name='accounting__entry_i_4a8a74_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='accountingentryline',
            unique_together={('entry', 'line_number')},
        ),
    ]
