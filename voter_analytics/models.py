from django.db import models

class Voter(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    street_num = models.IntegerField()
    street_name = models.TextField()
    apt_num = models.TextField(null=True, blank=True)
    zipcode = models.IntegerField()
    dob = models.TextField()
    dor = models.TextField()
    party = models.TextField()
    prec_num = models.TextField()
    
    v20s = models.BooleanField()
    v21t = models.BooleanField()
    v21p = models.BooleanField()
    v22g = models.BooleanField()
    v23t = models.BooleanField()
    voter_score = models.IntegerField()


    def __str__(self):
        '''Return a string representation of this Voter instance.'''
        return f'{self.first_name} {self.last_name} - Zipcode: {self.zipcode}, Party: {self.party}'


def load_data():
    '''Load data records from a CSV file.'''
    Voter.objects.all().delete()  # Start with an empty DB
    filename = '../newton_voters.csv'
    
    with open(filename, 'r') as f:
        headers = f.readline()  # Discard the header line
        for line in f:
            line = line.strip()  # Remove any surrounding whitespace from the line
            fields = [field.strip() for field in line.split(',')]
            try:
                result = Voter(
                    first_name=fields[1],
                    last_name=fields[2],
                    street_num=int(fields[3]) if fields[3] else None,
                    street_name=fields[4],
                    apt_num=fields[5] if fields[5] else None,
                    zipcode=int(fields[6]),
                    dob=fields[7],
                    dor=fields[8],
                    party=fields[9],
                    prec_num=fields[10],
                    v20s=(fields[11] == 'TRUE'),
                    v21t=(fields[12] == 'TRUE'),
                    v21p=(fields[13] == 'TRUE'),
                    v22g=(fields[14] == 'TRUE'),
                    v23t=(fields[15] == 'TRUE'),
                    voter_score=int(fields[16])
                )
                result.save()
                print(f'Created voter: {result}')
            except Exception as e:
                print(f"Exception occurred: {e}")
                print(f"Failed to process line: {line}")
