from datetime import datetime

from flask import url_for

from . import db

class Checkout(db.Model):
    __tablename__ = 'Checkouts'
    item_id = db.Column(db.Integer, db.ForeignKey('Items.id'), primary_key=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('Borrowers.id'), primary_key=True)
    date_borrowed = db.Column(db.DateTime, default=datetime.utcnow)
    date_returned = db.Column(db.DateTime, default=None)

    @property
    def serialize(self):
        return {
            'item_id': self.item_id,
            'borrower_id': self.borrower_id,
            'date_borrowed': self.date_borrowed,
            'date_returned': self.date_returned,
            #'active': self.is_active()
        }

    def is_active(self):
        return self.date_returned is None

    def __repr__(self):
        return f'<Checkout "{self.item.title}", "{self.borrower.name}">'

class Item(db.Model):
    __tablename__ = 'Items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    creator = db.Column(db.String(128))
    publisher = db.Column(db.String(64))
    location_id = db.Column(db.Integer, db.ForeignKey('Locations.id'))
    notes = db.Column(db.Text)
    loans = db.relationship('Checkout',
                            foreign_keys=[Checkout.item_id],
                            backref=db.backref('item', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'creator': self.creator,
            'publisher': self.publisher,
            # TODO: location
            'notes': self.notes,
            'available': self.is_available()
        }

    def is_available(self):
        return all([c.date_returned for c in Checkout.query.filter_by(item_id=self.id).all()])

    def __repr__(self):
        return f'<Item "{self.title}">'

class Borrower(db.Model):
    __tablename__ = 'Borrowers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    standing = db.Column(db.String(64))
    checkouts = db.relationship('Checkout',
                            foreign_keys=[Checkout.borrower_id],
                            backref=db.backref('borrower', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'standing': self.standing
        }

    def __repr__(self):
        return f'<Borrower "{self.name}">'

# maybe rename this to ItemRequest or something
class Acquisition(db.Model):
    __tablename__ = 'Acquisitions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    creator = db.Column(db.String(128))
    publisher = db.Column(db.String(64))
    status = db.Column(db.String(64))
    notes = db.Column(db.Text)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'creator': self.creator,
            'publisher': self.publisher,
            'status': self.status,
            'notes': self.notes
        }

    def __repr__(self):
        return f'<Acquisition "{self.title}">'

class Location(db.Model):
    __tablename__ = 'Locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    details = db.Column(db.Text)
    items = db.relationship('Item', backref='location')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'details': self.details
        }

    def __repr__(self):
        return f'<Location "{self.name}">'
