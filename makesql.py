""" Generate dynamic data extraction SQL for DataBuilder output files
---------------------------------------------------------------------

 Usage:
   makesql sqltemplate.sql dbname.db
"""

import sqlite3 as sq,argparse

parser = argparse.ArgumentParser()
parser.add_argument("sqlscript",help="File containing the static portion of the main SQL script")
parser.add_argument("dbfile",help="SQLite file generated by DataBuilder")
args = parser.parse_args()

def main(sqlscript, dbfile):
    con = sq.connect(dbfile)
    cur = con.cursor()
    # TODO: instead of relying on sqlite_denorm.sql, create the scaffold table from inside this 
    # script by putting the appropriate SQL commands into character strings and then passing those
    # strings as arguments to execute() (and capturing the result in a new variable, see below
    # for an example of cur.execute() usage (cur just happens to be what we named the cursor 
    # object we created above, and execute() is a method that cursor objects have)
    # TODO: instead of a with-clause temp-table create a static data dictionary table
    #		var(concept_path,concept_cd,ddomain,vid) but filter out certain facts 
    #		redundant with PATIENT_DIMENSION
    # TODO: the shortened column names will go into this data dictionary table
    # TODO: create a filtered static copy of OBSERVATION_FACT with a vid column, maybe others
    """
    The decision process
      branch node
	uses mods?
	  map modifiers; single column of semicolon-delimited code=mod pairs
	uses other columns?
	  UNKNOWN FALLBACK, single column
	code-only?
	  single column of semicolon-delimited codes
      leaf node
	code only?
	  single 1/0 column
	uses code and mods only?
	  map modifiers; single column of semicolon-delimited mods
	uses other columns?
	  any columns besides mods have more than one value per patient-date?
	    UNKNOWN FALLBACK, single column
	  otherwise
	    map modifiers; single column of semicolon-delimited mods named FOO_mod; for each additional BAR, one more column FOO_BAR
    
    TODO: implement a user-configurable 'rulebook' containing patterns for catching data that would otherwise fall 
    into UNKNOWN FALLBACK, and expressing in a parseable form what to do when each rule is triggered.
    TODO: The data dictionary will contain information about which built-in or user-configured rule applies for each vid
    We are probably looking at several different 'dcat' style tables, broken up by type of data
    TODO: We will iterate through the data dictionary, joining new columns to the result according to the applicable rule
    """
    # read in the SQLscript
    # use dbfile to generate lines to append to it
    # initialize the strings that will hold temp tables, selected columns, and joins
    tt = ''; sl = ''; js = ''
    # build a SQL query that, in one shot, returns the columns tt, sl, and js
    dynquery = \
        "select 'v'||substr('000'||id,-3,3)||'(pn, st, datconcat) " + \
        "as (select pn, st, datconcat from dcat2 where vid = '||id||')' tt," + \
        "'v'||substr('000'||id,-3,3)||'.datconcat v'||substr('000'||id,-3,3) sel," + \
        "'left join v'||substr('000'||id,-3,3)||' " + \
        "on v'||substr('000'||id,-3,3)||'.pn = patient_num " + \
        "and v'||substr('000'||id,-3,3)||'.st = start_date' js " + \
        "from variable where lower(name) not like '%old at visit' and name not in ('Living','Female','Male')"
    cur.execute(dynquery)
    rows = cur.fetchall()
    for row in rows[5:10]:
        tt += row[0]+','
        sl += row[1]+','
        js += row[2]+' '
    print "TEMP TABLE"
    print tt[:-1]
    print ' select patient_num, start_date,'
    print sl[:-1]
    print ' from scaffold '
    print js[:-1]
    # TODO: read in sqlscript, append these things to it, and run it, probably in chunks

if __name__ == '__main__':
    main(args.sqlscript,args.dbfile)


