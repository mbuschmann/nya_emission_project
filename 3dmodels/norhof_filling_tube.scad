l_outer = 30;
d_outer = 7;
wall_outer = 0.5;
l_fill = 50;
d_fill = 4;
wall_fill = 0.5;
hole_fill = 4;
l_probe = l_fill;
d_probe = 2;
wall_probe = 0.3;
hole_probe = 3;
endstop = 2;
h_hat = 5;
d_hat = 30;

// outer tube
translate([0,0,(l_fill-l_outer)/2]) difference(){
cylinder(h=l_outer, d=d_outer, $fn=100, center=true);
cylinder(h=l_outer+1, d=d_outer-(2*wall_outer), $fn=100, center=true);
};


// fill tube
translate([(d_outer-d_fill)/2,0,0]) difference(){
cylinder(h=l_fill, d=d_fill, $fn=100, center=true);
translate([0,0,endstop+0.1]) cylinder(h=l_fill-endstop, d=d_fill-(2*wall_fill), $fn=100, center=true);
translate([(d_outer-d_fill)/2,0,-l_fill/2+
    endstop+hole_fill/1.29]) cube([hole_fill/3,hole_fill/2,hole_fill], center=true);
};

// probe tube
translate([-(d_outer-d_probe)/2,0,0]) difference(){
cylinder(h=l_probe, d=d_probe, $fn=100, center=true);
translate([0,0,endstop+0.1]) cylinder(h=l_probe-endstop, d=d_probe-(2*wall_probe), $fn=100, center=true);
translate([-(d_probe)/2+0.2,0,-l_probe/2+
    endstop+hole_probe/1.15]) cube([hole_probe/3,hole_probe/2,hole_probe], center=true);
};

// hat
translate([0,0,l_outer/2-h_hat/2+(l_fill-l_outer)/2+0.01])
difference(){
    cylinder(d=d_hat, h=h_hat, $fn=100 ,center=true);
    cylinder(d=d_outer-0.1, h=h_hat+1, $fn=100 ,center=true);
};

// connection
translate([-0.9,0,0]) cube([1.8,1,l_fill], center=true);
